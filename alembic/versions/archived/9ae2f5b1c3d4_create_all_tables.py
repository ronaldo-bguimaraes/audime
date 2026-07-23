"""create_all_tables

Cria schemas e todas as tabelas do zero (idempotente via IF NOT EXISTS).

Esta migration é a verdadeira inicial — substitui a migration vazia
``8f830e7a6053`` e a ``cf76836d6914`` que tentava ALTER TABLE sem a
tabela existir. Em bancos já migrados é um no-op seguro.

Revision ID: 9ae2f5b1c3d4
Revises: cf76836d6914
Create Date: 2026-07-05 16:50:00.000000
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect
from sqlalchemy.dialects import postgresql

revision: str = "9ae2f5b1c3d4"
down_revision: Union[str, Sequence[str], None] = "cf76836d6914"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _is_sqlite() -> bool:
    bind = op.get_context().bind
    return bind.dialect.name == "sqlite" if bind else False


def _schema(name: str) -> dict:
    return {} if _is_sqlite() else {"schema": name}


def _tables_exist() -> bool:
    """Check whether core.usuario already exists (idempotency guard)."""
    bind = op.get_context().bind
    inspector = inspect(bind)
    if _is_sqlite():
        return "usuario" in inspector.get_table_names()
    return "usuario" in inspector.get_table_names(schema="core")


def upgrade() -> None:
    if _tables_exist():
        return  # Already migrated — no-op for existing databases

    is_sqlite = _is_sqlite()

    # ── 1. Schemas (PostgreSQL only) ────────────────────────────────
    if not is_sqlite:
        for schema in ("raw", "core", "staging", "analytics"):
            op.execute(f"CREATE SCHEMA IF NOT EXISTS {schema}")

    # ── 2. core.usuario ─────────────────────────────────────────────
    op.create_table(
        "usuario",
        sa.Column("id_usuario", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("nome", sa.String(), nullable=False),
        sa.Column("email", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id_usuario"),
        sa.UniqueConstraint("email"),
        **_schema("core"),
    )

    # ── 3. core.auth_code ───────────────────────────────────────────
    op.create_table(
        "auth_code",
        sa.Column("id_auth_code", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("email", sa.String(), nullable=False, index=True),
        sa.Column("code_hash", sa.String(64), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("used", sa.Boolean(), default=False),
        sa.Column("attempts", sa.Integer(), default=0),
        sa.Column("last_attempt_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id_auth_code"),
        **_schema("core"),
    )

    # ── 4. core.extracao (enum + table) ─────────────────────────────
    if not is_sqlite:
        op.execute("""
            DO $$
            BEGIN
                IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'extracao_status') THEN
                    CREATE TYPE core.extracao_status AS ENUM ('PENDING', 'RUNNING', 'DONE', 'ERROR');
                END IF;
            END
            $$;
        """)

    extracao_status_enum = sa.Enum(
        "PENDING", "RUNNING", "DONE", "ERROR",
        name="extracao_status",
        create_type=False,
    )
    op.create_table(
        "extracao",
        sa.Column("id_extracao", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column(
            "status",
            extracao_status_enum,
            nullable=False,
            server_default="PENDING",
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "id_usuario",
            sa.BigInteger(),
            sa.ForeignKey("core.usuario.id_usuario"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id_extracao"),
        **_schema("core"),
    )

    # ── 5. raw.importacao ───────────────────────────────────────────
    op.create_table(
        "importacao",
        sa.Column("id_importacao", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("storage_bucket", sa.String(63), nullable=False),
        sa.Column("storage_key", sa.Text(), nullable=False),
        sa.Column("storage_filename", sa.Text(), nullable=False),
        sa.Column("sha256", sa.String(64), nullable=False),
        sa.Column("imported_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "id_extracao",
            sa.BigInteger(),
            sa.ForeignKey("core.extracao.id_extracao"),
            nullable=True,
        ),
        sa.Column(
            "id_usuario",
            sa.BigInteger(),
            sa.ForeignKey("core.usuario.id_usuario"),
            nullable=True,
        ),
        sa.PrimaryKeyConstraint("id_importacao"),
        **_schema("raw"),
    )

    # ── 6. raw.fatura ───────────────────────────────────────────────
    op.create_table(
        "fatura",
        sa.Column("id_fatura", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("banco", sa.String(50), nullable=False),
        sa.Column("nome_titular", sa.Text(), nullable=False),
        sa.Column("mes_referencia", sa.Date(), nullable=True),
        sa.Column("extra", sa.JSON(), default={}),
        sa.Column("imported_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "id_usuario",
            sa.BigInteger(),
            sa.ForeignKey("core.usuario.id_usuario"),
            nullable=True,
        ),
        sa.Column(
            "id_importacao",
            sa.BigInteger(),
            sa.ForeignKey("raw.importacao.id_importacao"),
            nullable=True,
        ),
        sa.PrimaryKeyConstraint("id_fatura"),
        **_schema("raw"),
    )

    # ── 7. raw.transacao ────────────────────────────────────────────
    op.create_table(
        "transacao",
        sa.Column("id_transacao", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("data_realizacao", sa.Date(), nullable=False),
        sa.Column("descricao", sa.Text(), nullable=True),
        sa.Column("valor", sa.Numeric(8, 2), nullable=False),
        sa.Column("final_cartao", sa.String(4), nullable=True),
        sa.Column("parcela", sa.Text(), nullable=True),
        sa.Column("extra", sa.JSON(), default={}),
        sa.Column("imported_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "id_fatura",
            sa.BigInteger(),
            sa.ForeignKey("raw.fatura.id_fatura"),
            nullable=True,
        ),
        sa.Column(
            "id_importacao",
            sa.BigInteger(),
            sa.ForeignKey("raw.importacao.id_importacao"),
            nullable=True,
        ),
        sa.Column(
            "id_usuario",
            sa.BigInteger(),
            sa.ForeignKey("core.usuario.id_usuario"),
            nullable=True,
        ),
        sa.PrimaryKeyConstraint("id_transacao"),
        **_schema("raw"),
    )

    # ── 8. raw.nota ─────────────────────────────────────────────────
    op.create_table(
        "nota",
        sa.Column("id_nota", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("empresa", sa.Text(), nullable=False),
        sa.Column("chave", sa.String(44), nullable=False),
        sa.Column("numero", sa.Text(), nullable=False),
        sa.Column("serie", sa.Text(), nullable=False),
        sa.Column("emissao", sa.Date(), nullable=False),
        sa.Column("valor_total", sa.Numeric(10, 2), nullable=False),
        sa.Column("qtd_total_itens", sa.Integer(), nullable=True),
        sa.Column("extra", sa.JSON(), default={}),
        sa.Column("imported_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "id_usuario",
            sa.BigInteger(),
            sa.ForeignKey("core.usuario.id_usuario"),
            nullable=True,
        ),
        sa.Column(
            "id_fatura",
            sa.BigInteger(),
            sa.ForeignKey("raw.fatura.id_fatura"),
            nullable=True,
        ),
        sa.Column(
            "id_importacao",
            sa.BigInteger(),
            sa.ForeignKey("raw.importacao.id_importacao"),
            nullable=True,
        ),
        sa.PrimaryKeyConstraint("id_nota"),
        sa.UniqueConstraint("chave", "id_usuario", name="uq_nota_chave_usuario"),
        **_schema("raw"),
    )

    # ── 9. raw.item_nota (com item_valor_unidade nullable) ──────────
    op.create_table(
        "item_nota",
        sa.Column("id_item_nota", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("item_codigo", sa.Text(), nullable=True),
        sa.Column("item_descricao", sa.Text(), nullable=False),
        sa.Column("item_quantidade", sa.Numeric(10, 3), nullable=False, server_default="1"),
        sa.Column("item_tipo_unidade", sa.Text(), nullable=True, server_default="UN"),
        sa.Column("item_valor_unidade", sa.Numeric(10, 2), nullable=True),
        sa.Column("item_valor_total", sa.Numeric(10, 2), nullable=False),
        sa.Column("extra", sa.JSON(), default={}),
        sa.Column("imported_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "id_nota",
            sa.BigInteger(),
            sa.ForeignKey("raw.nota.id_nota"),
            nullable=True,
        ),
        sa.Column(
            "id_usuario",
            sa.BigInteger(),
            sa.ForeignKey("core.usuario.id_usuario"),
            nullable=True,
        ),
        sa.PrimaryKeyConstraint("id_item_nota"),
        **_schema("raw"),
    )

    # ── 10. staging.nota_normalizada ────────────────────────────────
    op.create_table(
        "nota_normalizada",
        sa.Column("id_nota_normalizada", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column(
            "id_nota",
            sa.BigInteger(),
            sa.ForeignKey("raw.nota.id_nota"),
            nullable=True,
        ),
        sa.Column(
            "id_usuario",
            sa.BigInteger(),
            sa.ForeignKey("core.usuario.id_usuario"),
            nullable=True,
        ),
        sa.Column("valor_total", sa.Numeric(10, 2), nullable=False),
        sa.Column("emitente", sa.Text(), nullable=False),
        sa.Column("data_emissao", sa.Date(), nullable=False),
        sa.Column("chave_acesso", sa.String(44), nullable=False),
        sa.Column("processado_em", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id_nota_normalizada"),
        **_schema("staging"),
    )

    # ── 11. staging.item_normalizado ────────────────────────────────
    op.create_table(
        "item_normalizado",
        sa.Column("id_item_normalizado", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column(
            "id_item_nota",
            sa.BigInteger(),
            sa.ForeignKey("raw.item_nota.id_item_nota"),
            nullable=True,
        ),
        sa.Column(
            "id_nota_normalizada",
            sa.BigInteger(),
            sa.ForeignKey("staging.nota_normalizada.id_nota_normalizada"),
            nullable=True,
        ),
        sa.Column(
            "id_usuario",
            sa.BigInteger(),
            sa.ForeignKey("core.usuario.id_usuario"),
            nullable=True,
        ),
        sa.Column("descricao", sa.Text(), nullable=False),
        sa.Column("quantidade", sa.Numeric(10, 3), nullable=False),
        sa.Column("valor_unitario", sa.Numeric(10, 2), nullable=False),
        sa.Column("valor_total", sa.Numeric(10, 2), nullable=False),
        sa.Column("processado_em", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id_item_normalizado"),
        **_schema("staging"),
    )

    # ── 12. analytics.gasto_mensal ──────────────────────────────────
    op.create_table(
        "gasto_mensal",
        sa.Column("id_gasto_mensal", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column(
            "id_usuario",
            sa.BigInteger(),
            sa.ForeignKey("core.usuario.id_usuario"),
            nullable=True,
        ),
        sa.Column("mes_ano", sa.Date(), nullable=False),
        sa.Column("total_gasto", sa.Numeric(12, 2), nullable=False, server_default="0"),
        sa.Column("qtd_transacoes", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("qtd_notas", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("atualizado_em", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id_gasto_mensal"),
        **_schema("analytics"),
    )

    # ── 13. analytics.gasto_categoria ───────────────────────────────
    op.create_table(
        "gasto_categoria",
        sa.Column("id_gasto_categoria", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column(
            "id_usuario",
            sa.BigInteger(),
            sa.ForeignKey("core.usuario.id_usuario"),
            nullable=True,
        ),
        sa.Column("categoria", sa.Text(), nullable=False),
        sa.Column("mes_ano", sa.Date(), nullable=False),
        sa.Column("total_gasto", sa.Numeric(12, 2), nullable=False, server_default="0"),
        sa.Column("qtd_itens", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("atualizado_em", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id_gasto_categoria"),
        **_schema("analytics"),
    )


def downgrade() -> None:
    if _tables_exist():
        return  # Tables existed before this migration — don't drop

    is_sqlite = _is_sqlite()

    def _no_schema(name: str) -> dict:
        return {"schema": name} if not is_sqlite else {}

    op.drop_table("gasto_categoria", **_no_schema("analytics"))
    op.drop_table("gasto_mensal", **_no_schema("analytics"))
    op.drop_table("item_normalizado", **_no_schema("staging"))
    op.drop_table("nota_normalizada", **_no_schema("staging"))
    op.drop_table("item_nota", **_no_schema("raw"))
    op.drop_table("nota", **_no_schema("raw"))
    op.drop_table("transacao", **_no_schema("raw"))
    op.drop_table("fatura", **_no_schema("raw"))
    op.drop_table("importacao", **_no_schema("raw"))
    op.drop_table("extracao", **_no_schema("core"))
    op.drop_table("auth_code", **_no_schema("core"))
    op.drop_table("usuario", **_no_schema("core"))

    if not is_sqlite:
        op.execute("DROP TYPE IF EXISTS core.extracao_status")
