import sqlalchemy as sa

from database import Base
from database.models.utils import pg_timestampz
from extracao.enum.status import ExtracaoStatus


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
    usuario = sa.orm.relationship("Usuario", back_populates="extracoes")
