import sqlalchemy as sa
from sqlalchemy.orm import relationship

from abstract.base import Base, pg_timestampz


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


class NotaAnalytics(Base):
    __tablename__ = "nota_analytics"
    __table_args__ = {"schema": "analytics"}

    id_nota_analytics = sa.Column(sa.BigInteger, primary_key=True)
    id_extracao = sa.Column(sa.BigInteger, nullable=False)
    id_usuario = sa.Column(sa.BigInteger, sa.ForeignKey("core.usuario.id_usuario"))
    chave_acesso = sa.Column(sa.String(44), nullable=True)
    empresa = sa.Column(sa.Text, nullable=True)
    numero = sa.Column(sa.Text, nullable=True)
    serie = sa.Column(sa.Text, nullable=True)
    emissao = sa.Column(sa.Date, nullable=True)
    valor_total = sa.Column(sa.Numeric(12, 2), nullable=True)
    qtd_total_itens = sa.Column(sa.Integer, nullable=True)
    extra = sa.Column(sa.JSON, nullable=True)

    # Soft delete / ativo
    is_active = sa.Column(sa.Boolean, nullable=False, default=True)

    # SCD Type 2 columns
    valid_from = sa.Column(sa.DateTime(timezone=True), nullable=False)
    valid_to = sa.Column(sa.DateTime(timezone=True), nullable=True)
    is_current = sa.Column(sa.Boolean, nullable=False, default=True)

    # Lineage
    id_importacao = sa.Column(sa.BigInteger, nullable=True)
    id_nota_raw = sa.Column(sa.BigInteger, nullable=True)
    processado_em = pg_timestampz()

    items = relationship("ItemNotaAnalytics", backref="nota", lazy="selectin")


class ItemNotaAnalytics(Base):
    __tablename__ = "item_nota_analytics"
    __table_args__ = {"schema": "analytics"}

    id_item_analytics = sa.Column(sa.BigInteger, primary_key=True)
    id_nota_analytics = sa.Column(sa.BigInteger, sa.ForeignKey("analytics.nota_analytics.id_nota_analytics"))
    descricao = sa.Column(sa.Text, nullable=True)
    quantidade = sa.Column(sa.Numeric(10, 3), nullable=True)
    unidade = sa.Column(sa.Text, nullable=True)
    valor_unitario = sa.Column(sa.Numeric(10, 2), nullable=True)
    valor_total = sa.Column(sa.Numeric(10, 2), nullable=True)
    processado_em = pg_timestampz()
