"""make_item_valor_unidade_nullable

Revision ID: cf76836d6914
Revises: 8f830e7a6053
Create Date: 2026-07-05 10:59:35.897787

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'cf76836d6914'
down_revision: Union[str, Sequence[str], None] = '8f830e7a6053'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_context().bind
    is_sqlite = bind.dialect.name == "sqlite" if bind else False
    schema = None if is_sqlite else "raw"
    with op.batch_alter_table("item_nota", schema=schema) as batch_op:
        batch_op.alter_column("item_valor_unidade", nullable=True)


def downgrade() -> None:
    bind = op.get_context().bind
    is_sqlite = bind.dialect.name == "sqlite" if bind else False
    schema = None if is_sqlite else "raw"
    with op.batch_alter_table("item_nota", schema=schema) as batch_op:
        batch_op.alter_column("item_valor_unidade", nullable=False)
