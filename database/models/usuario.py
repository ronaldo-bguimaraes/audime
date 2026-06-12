import sqlalchemy as sa

from database import Base
from database.models.utils import pg_timestampz


class Usuario(Base):
    __tablename__ = "usuario"
    __table_args__ = {"schema": "core"}

    id_usuario = sa.Column(sa.BigInteger, primary_key=True)
    nome = sa.Column(sa.String, nullable=False)
    email = sa.Column(sa.String, nullable=False, unique=True)
    created_at = pg_timestampz()
    updated_at = pg_timestampz()
    extracoes = sa.orm.relationship("Extracao", back_populates="usuario")
