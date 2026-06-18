import sqlalchemy as sa

from abstract.base import Base, pg_timestampz


class NotaNormalizada(Base):
    __tablename__ = "nota_normalizada"
    __table_args__ = {"schema": "staging"}

    id_nota_normalizada = sa.Column(sa.BigInteger, primary_key=True)
    id_nota = sa.Column(sa.BigInteger, sa.ForeignKey("raw.nota.id_nota"))
    id_usuario = sa.Column(sa.BigInteger, sa.ForeignKey("core.usuario.id_usuario"))
    valor_total = sa.Column(sa.Numeric(10, 2), nullable=False)
    emitente = sa.Column(sa.Text, nullable=False)
    data_emissao = sa.Column(sa.Date, nullable=False)
    chave_acesso = sa.Column(sa.String(44), nullable=False)
    processado_em = pg_timestampz()


class ItemNormalizado(Base):
    __tablename__ = "item_normalizado"
    __table_args__ = {"schema": "staging"}

    id_item_normalizado = sa.Column(sa.BigInteger, primary_key=True)
    id_item_nota = sa.Column(sa.BigInteger, sa.ForeignKey("raw.item_nota.id_item_nota"))
    id_nota_normalizada = sa.Column(sa.BigInteger, sa.ForeignKey("staging.nota_normalizada.id_nota_normalizada"))
    id_usuario = sa.Column(sa.BigInteger, sa.ForeignKey("core.usuario.id_usuario"))
    descricao = sa.Column(sa.Text, nullable=False)
    quantidade = sa.Column(sa.Numeric(10, 3), nullable=False)
    valor_unitario = sa.Column(sa.Numeric(10, 2), nullable=False)
    valor_total = sa.Column(sa.Numeric(10, 2), nullable=False)
    processado_em = pg_timestampz()
