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
    """No-op: ``item_valor_unidade`` is already nullable in ``9ae2f5b1c3d4``."""
    return


def downgrade() -> None:
    """No-op: the column definition lives in the ``9ae2f5b1c3d4`` CREATE TABLE."""
    return
