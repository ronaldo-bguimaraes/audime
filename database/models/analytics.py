import sqlalchemy as sa

from database.base import Base, pg_timestampz


class GastoMensal(Base):
    __tablename__ = "gasto_mensal"
    __table_args__ = {"schema": "analytics"}

    id_gasto_mensal = sa.Column(sa.BigInteger, primary_key=True)
    id_usuario = sa.Column(sa.BigInteger, sa.ForeignKey("core.usuario.id_usuario"))
    mes_ano = sa.Column(sa.Date, nullable=False)
    total_gasto = sa.Column(sa.Numeric(12, 2), nullable=False, default=0)
    qtd_transacoes = sa.Column(sa.Integer, nullable=False, default=0)
    qtd_notas = sa.Column(sa.Integer, nullable=False, default=0)
    atualizado_em = pg_timestampz()


class GastoCategoria(Base):
    __tablename__ = "gasto_categoria"
    __table_args__ = {"schema": "analytics"}

    id_gasto_categoria = sa.Column(sa.BigInteger, primary_key=True)
    id_usuario = sa.Column(sa.BigInteger, sa.ForeignKey("core.usuario.id_usuario"))
    categoria = sa.Column(sa.Text, nullable=False)
    mes_ano = sa.Column(sa.Date, nullable=False)
    total_gasto = sa.Column(sa.Numeric(12, 2), nullable=False, default=0)
    qtd_itens = sa.Column(sa.Integer, nullable=False, default=0)
    atualizado_em = pg_timestampz()
