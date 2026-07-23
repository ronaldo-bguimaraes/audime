from enum import Enum

import sqlalchemy as sa
from sqlalchemy.orm import relationship

from abstract.base import Base, pg_timestampz


class ExtracaoStatus(Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    DONE = "DONE"
    ERROR = "ERROR"


class StepStatus(Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    DONE = "DONE"
    ERROR = "ERROR"


class PipelineStep(Enum):
    RAW_IMPORT = "RAW_IMPORT"
    STAGING = "STAGING"
    ANALYTICS = "ANALYTICS"
    COMPLETE = "COMPLETE"


class Usuario(Base):
    __tablename__ = "usuario"
    __table_args__ = {"schema": "core"}

    id_usuario = sa.Column(sa.BigInteger().with_variant(sa.Integer(), "sqlite"), primary_key=True)
    nome = sa.Column(sa.String, nullable=False)
    email = sa.Column(sa.String, nullable=False, unique=True)
    created_at = pg_timestampz()
    updated_at = pg_timestampz()


class Extracao(Base):
    __tablename__ = "extracao"
    __table_args__ = {"schema": "core"}

    id_extracao = sa.Column(
        sa.BigInteger().with_variant(sa.Integer(), "sqlite"), primary_key=True
    )
    url = sa.Column(sa.Text, nullable=True)
    status = sa.Column(
        sa.Enum(ExtracaoStatus, name="extracao_status", schema="core", create_type=False),
        nullable=False,
        default=ExtracaoStatus.PENDING,
        server_default="PENDING",
    )
    created_at = pg_timestampz()
    reprocess_count = sa.Column(sa.Integer, default=0, nullable=True, server_default="0")
    reprocessed_at = sa.Column(sa.DateTime(timezone=True), nullable=True)
    id_usuario = sa.Column(sa.BigInteger, sa.ForeignKey("core.usuario.id_usuario"), nullable=False)

    steps = relationship("ExtracaoStep", backref="extracao", lazy="selectin",
                         order_by="ExtracaoStep.ordem")


class ExtracaoStep(Base):
    __tablename__ = "extracao_step"
    __table_args__ = {"schema": "core"}

    id_step = sa.Column(
        sa.BigInteger().with_variant(sa.Integer(), "sqlite"), primary_key=True
    )
    id_extracao = sa.Column(
        sa.BigInteger, sa.ForeignKey("core.extracao.id_extracao"), nullable=False
    )
    etapa = sa.Column(
        sa.Enum(PipelineStep, name="pipeline_step", schema="core", create_type=False),
        nullable=False,
    )
    status = sa.Column(
        sa.Enum(StepStatus, name="step_status", schema="core", create_type=False),
        nullable=False,
        default=StepStatus.PENDING,
    )
    ordem = sa.Column(sa.Integer, nullable=False, default=0)
    iniciado_em = sa.Column(sa.DateTime(timezone=True), nullable=True)
    concluido_em = sa.Column(sa.DateTime(timezone=True), nullable=True)
    mensagem = sa.Column(sa.Text, nullable=True)
