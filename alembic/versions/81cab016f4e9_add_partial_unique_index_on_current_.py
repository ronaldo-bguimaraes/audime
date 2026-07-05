"""add partial unique index on current analytics (id_usuario, chave_acesso)

Replaces the previous unique index on (id_extracao) with one on
(id_usuario, chave_acesso) to enforce one current SCD2 version
per user+chave.

Revision ID: 81cab016f4e9
Revises: a149e73f7253
Create Date: 2026-07-05 17:45:05.546452

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "81cab016f4e9"
down_revision: Union[str, Sequence[str], None] = "a149e73f7253"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _is_sqlite() -> bool:
    bind = op.get_context().bind
    return bind.dialect.name == "sqlite" if bind else False


def upgrade() -> None:
    is_sqlite = _is_sqlite()

    if not is_sqlite:
        op.execute("DROP INDEX IF EXISTS analytics.uq_analytics_nota_current")
        op.execute("""
            CREATE UNIQUE INDEX IF NOT EXISTS ix_nota_analytics_current_unique
            ON analytics.nota_analytics (id_usuario, chave_acesso)
            WHERE is_current = TRUE
        """)


def downgrade() -> None:
    is_sqlite = _is_sqlite()

    if not is_sqlite:
        op.execute("DROP INDEX IF EXISTS analytics.ix_nota_analytics_current_unique")
        op.execute("""
            CREATE UNIQUE INDEX IF NOT EXISTS uq_analytics_nota_current
            ON analytics.nota_analytics (id_extracao)
            WHERE is_current = TRUE
        """)
