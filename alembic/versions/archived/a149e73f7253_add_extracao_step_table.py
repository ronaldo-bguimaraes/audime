"""add_extracao_step_table

Adds the core.extracao_step table for pipeline checklist tracking.

Revision ID: a149e73f7253
Revises: b4c2a1d3e5f6
Create Date: 2026-07-05 16:58:14.872498

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'a149e73f7253'
down_revision: Union[str, Sequence[str], None] = 'b4c2a1d3e5f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'pipeline_step') THEN
                CREATE TYPE core.pipeline_step AS ENUM ('RAW_IMPORT', 'STAGING', 'ANALYTICS', 'COMPLETE');
            END IF;
            IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'step_status') THEN
                CREATE TYPE core.step_status AS ENUM ('PENDING', 'RUNNING', 'DONE', 'ERROR');
            END IF;
        END
        $$;
    """)
    op.create_table('extracao_step',
        sa.Column('id_step', sa.BigInteger().with_variant(sa.Integer(), 'sqlite'), nullable=False),
        sa.Column('id_extracao', sa.BigInteger(), nullable=False),
        sa.Column('etapa', sa.Enum('RAW_IMPORT', 'STAGING', 'ANALYTICS', 'COMPLETE', name='pipeline_step', schema='core', create_type=False), nullable=False),
        sa.Column('status', sa.Enum('PENDING', 'RUNNING', 'DONE', 'ERROR', name='step_status', schema='core', create_type=False), nullable=False),
        sa.Column('ordem', sa.Integer(), nullable=False),
        sa.Column('iniciado_em', sa.DateTime(timezone=True), nullable=True),
        sa.Column('concluido_em', sa.DateTime(timezone=True), nullable=True),
        sa.Column('mensagem', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['id_extracao'], ['core.extracao.id_extracao']),
        sa.PrimaryKeyConstraint('id_step'),
        schema='core',
    )


def downgrade() -> None:
    op.drop_table('extracao_step', schema='core')
