"""make_item_normalizado_valor_unitario_nullable

Revision ID: d312479b0381
Revises: ea7f3d2b1c5a
Create Date: 2026-07-05 18:47:38.062411

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


revision: str = 'd312479b0381'
down_revision: Union[str, Sequence[str], None] = 'ea7f3d2b1c5a'
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
    if _is_sqlite():
        return
    if _has_column("item_normalizado", "valor_unitario", schema="staging"):
        op.alter_column(
            "item_normalizado",
            "valor_unitario",
            existing_type=sa.NUMERIC(precision=10, scale=2),
            nullable=True,
            **_schema("staging"),
        )


def downgrade() -> None:
    if _is_sqlite():
        return
    if _has_column("item_normalizado", "valor_unitario", schema="staging"):
        op.alter_column(
            "item_normalizado",
            "valor_unitario",
            existing_type=sa.NUMERIC(precision=10, scale=2),
            nullable=False,
            **_schema("staging"),
        )
