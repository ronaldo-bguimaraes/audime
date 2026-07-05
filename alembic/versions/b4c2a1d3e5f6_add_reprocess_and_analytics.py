"""add_reprocess_and_analytics

Adds reprocess columns to core.extracao, creates staging columns,
creates analytics SCD2 tables, and removes UNIQUE constraint from raw.nota.

Revision ID: b4c2a1d3e5f6
Revises: 8a3f7e2c9d1b
Create Date: 2026-07-05 18:00:00.000000
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect
from sqlalchemy.dialects import postgresql

revision: str = "b4c2a1d3e5f6"
down_revision: Union[str, Sequence[str], None] = "8a3f7e2c9d1b"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _is_sqlite() -> bool:
    bind = op.get_context().bind
    return bind.dialect.name == "sqlite" if bind else False


def _schema(name: str) -> dict:
    return {} if _is_sqlite() else {"schema": name}


def _has_column(table: str, column: str, schema: str | None = None) -> bool:
    bind = op.get_context().bind
    inspector = inspect(bind)
    if _is_sqlite():
        cols = inspector.get_columns(table)
    else:
        cols = inspector.get_columns(table, schema=schema)
    return any(c["name"] == column for c in cols)


def _has_constraint(table: str, constraint: str, schema: str | None = None) -> bool:
    bind = op.get_context().bind
    inspector = inspect(bind)
    if _is_sqlite():
        cons_list = inspector.get_unique_constraints(table)
    else:
        cons_list = inspector.get_unique_constraints(table, schema=schema)
    for cons in cons_list:
        if cons["name"] == constraint:
            return True
    return False


def upgrade() -> None:
    is_sqlite = _is_sqlite()

    # ── 1. Add reprocess columns to core.extracao ────────────────────
    if not _has_column("extracao", "reprocess_count", schema="core"):
        op.add_column(
            "extracao",
            sa.Column("reprocess_count", sa.Integer(), server_default="0", nullable=True),
            **_schema("core"),
        )
    if not _has_column("extracao", "reprocessed_at", schema="core"):
        op.add_column(
            "extracao",
            sa.Column("reprocessed_at", sa.DateTime(timezone=True), nullable=True),
            **_schema("core"),
        )

    # ── 2. Drop UNIQUE(chave, id_usuario) from raw.nota ──────────────
    # SQLite does not support ALTER TABLE DROP CONSTRAINT,
    # but the model no longer defines the constraint, so new SQLite
    # tables created via create_all won't have it.
    if not is_sqlite and _has_constraint("nota", "uq_nota_chave_usuario", schema="raw"):
        op.drop_constraint("uq_nota_chave_usuario", "nota", schema="raw", type_="unique")

    # ── 3. Add columns to staging.nota_normalizada ───────────────────
    if not _has_column("nota_normalizada", "id_importacao", schema="staging"):
        col_type = sa.BigInteger()
        if not is_sqlite:
            col_type = sa.BigInteger()
        op.add_column(
            "nota_normalizada",
            sa.Column("id_importacao", sa.BigInteger(), nullable=True),
            **_schema("staging"),
        )
    if not _has_column("nota_normalizada", "id_extracao", schema="staging"):
        op.add_column(
            "nota_normalizada",
            sa.Column("id_extracao", sa.BigInteger(), nullable=True),
            **_schema("staging"),
        )

    # ── 4. Create analytics tables (SCD2) ────────────────────────────
    if not is_sqlite:
        # Ensure analytics schema exists (idempotent)
        op.execute("CREATE SCHEMA IF NOT EXISTS analytics")

    op.create_table(
        "nota_analytics",
        sa.Column("id_nota_analytics", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("id_extracao", sa.BigInteger(), nullable=False),
        sa.Column("id_usuario", sa.BigInteger(), nullable=True),
        sa.Column("chave_acesso", sa.String(44), nullable=True),
        sa.Column("empresa", sa.Text(), nullable=True),
        sa.Column("numero", sa.Text(), nullable=True),
        sa.Column("serie", sa.Text(), nullable=True),
        sa.Column("emissao", sa.Date(), nullable=True),
        sa.Column("valor_total", sa.Numeric(12, 2), nullable=True),
        sa.Column("qtd_total_itens", sa.Integer(), nullable=True),
        sa.Column("extra", sa.JSON(), nullable=True),
        # SCD2 columns
        sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("valid_from", sa.DateTime(timezone=True), nullable=False),
        sa.Column("valid_to", sa.DateTime(timezone=True), nullable=True),
        sa.Column("is_current", sa.Boolean(), nullable=False, server_default="true"),
        # Lineage
        sa.Column("id_importacao", sa.BigInteger(), nullable=True),
        sa.Column("id_nota_raw", sa.BigInteger(), nullable=True),
        sa.Column("processado_em", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id_nota_analytics"),
        sa.ForeignKeyConstraint(["id_usuario"], ["core.usuario.id_usuario"], name="fk_analytics_nota_usuario"),
        **_schema("analytics"),
    )

    op.create_table(
        "item_nota_analytics",
        sa.Column("id_item_analytics", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("id_nota_analytics", sa.BigInteger(), nullable=False),
        sa.Column("descricao", sa.Text(), nullable=True),
        sa.Column("quantidade", sa.Numeric(10, 3), nullable=True),
        sa.Column("unidade", sa.Text(), nullable=True),
        sa.Column("valor_unitario", sa.Numeric(10, 2), nullable=True),
        sa.Column("valor_total", sa.Numeric(10, 2), nullable=True),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("processado_em", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id_item_analytics"),
        sa.ForeignKeyConstraint(
            ["id_nota_analytics"], ["analytics.nota_analytics.id_nota_analytics"],
            name="fk_analytics_item_nota",
        ),
        **_schema("analytics"),
    )

    # Partial unique index: only one current version per extraction
    if not is_sqlite:
        op.execute("""
            CREATE UNIQUE INDEX IF NOT EXISTS uq_analytics_nota_current
            ON analytics.nota_analytics (id_extracao) WHERE is_current = TRUE
        """)


def downgrade() -> None:
    is_sqlite = _is_sqlite()

    # Drop analytics tables
    op.drop_table("item_nota_analytics", **_schema("analytics"))
    op.drop_table("nota_analytics", **_schema("analytics"))

    # Drop partial index (PostgreSQL)
    if not is_sqlite:
        op.execute("DROP INDEX IF EXISTS analytics.uq_analytics_nota_current")


    # Remove staging columns
    if _has_column("nota_normalizada", "id_extracao", schema="staging"):
        op.drop_column("nota_normalizada", "id_extracao", **_schema("staging"))
    if _has_column("nota_normalizada", "id_importacao", schema="staging"):
        op.drop_column("nota_normalizada", "id_importacao", **_schema("staging"))

    # Restore UNIQUE constraint on raw.nota (PostgreSQL only)
    if not is_sqlite and not _has_constraint("nota", "uq_nota_chave_usuario", schema="raw"):
        op.create_unique_constraint(
            "uq_nota_chave_usuario",
            "nota",
            ["chave", "id_usuario"],
            **_schema("raw"),
        )

    # Remove reprocess columns
    if _has_column("extracao", "reprocessed_at", schema="core"):
        op.drop_column("extracao", "reprocessed_at", **_schema("core"))
    if _has_column("extracao", "reprocess_count", schema="core"):
        op.drop_column("extracao", "reprocess_count", **_schema("core"))
