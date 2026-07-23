"""remove_version_columns

Revision ID: fc2e4c89057c
Revises: a149e73f7253
Create Date: 2026-07-05 18:19:54.290865

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


revision: str = 'fc2e4c89057c'
down_revision: Union[str, Sequence[str], None] = 'a149e73f7253'
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


def upgrade() -> None:
    if _has_column("item_nota_analytics", "version", schema="analytics"):
        op.drop_column("item_nota_analytics", "version", **_schema("analytics"))

    if _has_column("nota_analytics", "version", schema="analytics"):
        if not _is_sqlite():
            op.drop_index(
                op.f("uq_analytics_nota_current"),
                table_name="nota_analytics",
                schema="analytics",
                postgresql_where="(is_current = true)",
            )
        op.drop_column("nota_analytics", "version", **_schema("analytics"))


def downgrade() -> None:
    op.add_column(
        "nota_analytics",
        sa.Column("version", sa.INTEGER(), server_default=sa.text("1"), autoincrement=False, nullable=False),
        **_schema("analytics"),
    )
    if not _is_sqlite():
        op.create_index(
            op.f("uq_analytics_nota_current"),
            "nota_analytics",
            ["id_extracao"],
            unique=True,
            schema="analytics",
            postgresql_where="(is_current = true)",
        )
    op.add_column(
        "item_nota_analytics",
        sa.Column("version", sa.INTEGER(), autoincrement=False, nullable=False),
        **_schema("analytics"),
    )
