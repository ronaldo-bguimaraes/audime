from enum import Enum

import sqlalchemy as sa

from abstract.base import Base, pg_timestampz


class ExtracaoStatus(Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    DONE = "DONE"
    ERROR = "ERROR"


class Usuario(Base):
    __tablename__ = "usuario"
    __table_args__ = {"schema": "core"}

    id_usuario = sa.Column(sa.BigInteger, primary_key=True)
    nome = sa.Column(sa.String, nullable=False)
    email = sa.Column(sa.String, nullable=False, unique=True)
    created_at = pg_timestampz()
    updated_at = pg_timestampz()


class Extracao(Base):
    __tablename__ = "extracao"
    __table_args__ = {"schema": "core"}

    id_extracao = sa.Column(sa.BigInteger, primary_key=True)
    status = sa.Column(
        sa.Enum(ExtracaoStatus, name="extracao_status", schema="core", create_type=False),
        nullable=False,
        default=ExtracaoStatus.PENDING,
    )
    created_at = pg_timestampz()
    id_usuario = sa.Column(sa.BigInteger, sa.ForeignKey("core.usuario.id_usuario"))
