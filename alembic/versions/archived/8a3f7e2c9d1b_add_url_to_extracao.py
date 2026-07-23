"""add_url_to_extracao

Adds a nullable ``url`` column to the ``extracao`` table.
Compatible with PostgreSQL and SQLite (idempotent).

Revision ID: 8a3f7e2c9d1b
Revises: 9ae2f5b1c3d4
Create Date: 2026-07-05 17:00:00.000000
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "8a3f7e2c9d1b"
down_revision: Union[str, Sequence[str], None] = "9ae2f5b1c3d4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _is_sqlite() -> bool:
    bind = op.get_context().bind
    return bind.dialect.name == "sqlite" if bind else False


def _schema() -> dict:
    return {} if _is_sqlite() else {"schema": "core"}


def upgrade() -> None:
    op.add_column(
        "extracao",
        sa.Column("url", sa.Text(), nullable=True),
        **_schema(),
    )


def downgrade() -> None:
    op.drop_column("extracao", "url", **_schema())
