"""add_is_active_to_nota_analytics

Adds is_active boolean column to analytics.nota_analytics for soft delete.

Revision ID: ea7f3d2b1c5a
Revises: fc2e4c89057c
Create Date: 2026-07-05 18:30:00.000000
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

revision: str = "ea7f3d2b1c5a"
down_revision: Union[str, Sequence[str], None] = "fc2e4c89057c"
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
    is_sqlite = _is_sqlite()

    if not _has_column("nota_analytics", "is_active", schema="analytics"):
        op.add_column(
            "nota_analytics",
            sa.Column(
                "is_active",
                sa.Boolean(),
                nullable=False,
                server_default=sa.sql.expression.true() if not is_sqlite else "1",
            ),
            **_schema("analytics"),
        )


def downgrade() -> None:
    if _has_column("nota_analytics", "is_active", schema="analytics"):
        op.drop_column("nota_analytics", "is_active", **_schema("analytics"))
