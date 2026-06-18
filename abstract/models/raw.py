import sqlalchemy as sa

from abstract.base import Base, pg_timestampz


class Importacao(Base):
    __tablename__ = "importacao"
    __table_args__ = {"schema": "raw"}

    id_importacao = sa.Column(sa.BigInteger, primary_key=True)
    storage_bucket = sa.Column(sa.String(63), nullable=False)
    storage_key = sa.Column(sa.Text, nullable=False)
    storage_filename = sa.Column(sa.Text, nullable=False)
    sha256 = sa.Column(sa.String(64), nullable=False)
    imported_at = pg_timestampz()
    id_extracao = sa.Column(sa.BigInteger, sa.ForeignKey("core.extracao.id_extracao"))
    id_usuario = sa.Column(sa.BigInteger, sa.ForeignKey("core.usuario.id_usuario"))


class Fatura(Base):
    __tablename__ = "fatura"
    __table_args__ = {"schema": "raw"}

    id_fatura = sa.Column(sa.BigInteger, primary_key=True)
    banco = sa.Column(sa.String(50), nullable=False)
    nome_titular = sa.Column(sa.Text, nullable=False)
    mes_referencia = sa.Column(sa.Date)
    extra = sa.Column(sa.JSONB, default={})
    imported_at = pg_timestampz()
    id_usuario = sa.Column(sa.BigInteger, sa.ForeignKey("core.usuario.id_usuario"))
    id_importacao = sa.Column(sa.BigInteger, sa.ForeignKey("raw.importacao.id_importacao"))


class Transacao(Base):
    __tablename__ = "transacao"
    __table_args__ = {"schema": "raw"}

    id_transacao = sa.Column(sa.BigInteger, primary_key=True)
    data_realizacao = sa.Column(sa.Date, nullable=False)
    descricao = sa.Column(sa.Text)
    valor = sa.Column(sa.Numeric(8, 2), nullable=False)
    final_cartao = sa.Column(sa.String(4))
    parcela = sa.Column(sa.Text)
    extra = sa.Column(sa.JSONB, default={})
    imported_at = pg_timestampz()
    id_fatura = sa.Column(sa.BigInteger, sa.ForeignKey("raw.fatura.id_fatura"))
    id_importacao = sa.Column(sa.BigInteger, sa.ForeignKey("raw.importacao.id_importacao"))
    id_usuario = sa.Column(sa.BigInteger, sa.ForeignKey("core.usuario.id_usuario"))


class Nota(Base):
    __tablename__ = "nota"
    __table_args__ = {"schema": "raw"}

    id_nota = sa.Column(sa.BigInteger, primary_key=True)
    empresa = sa.Column(sa.Text, nullable=False)
    chave = sa.Column(sa.String(44), nullable=False, unique=True)
    numero = sa.Column(sa.Text, nullable=False)
    serie = sa.Column(sa.Text, nullable=False)
    emissao = sa.Column(sa.Date, nullable=False)
    valor_total = sa.Column(sa.Numeric(10, 2), nullable=False)
    extra = sa.Column(sa.JSONB, default={})
    imported_at = pg_timestampz()
    id_usuario = sa.Column(sa.BigInteger, sa.ForeignKey("core.usuario.id_usuario"))
    id_fatura = sa.Column(sa.BigInteger, sa.ForeignKey("raw.fatura.id_fatura"))
    id_importacao = sa.Column(sa.BigInteger, sa.ForeignKey("raw.importacao.id_importacao"))


class ItemNota(Base):
    __tablename__ = "item_nota"
    __table_args__ = {"schema": "raw"}

    id_item_nota = sa.Column(sa.BigInteger, primary_key=True)
    item_codigo = sa.Column(sa.Text)
    item_descricao = sa.Column(sa.Text, nullable=False)
    item_quantidade = sa.Column(sa.Numeric(10, 3), nullable=False, default=1)
    item_tipo_unidade = sa.Column(sa.Text, default="UN")
    item_valor_unidade = sa.Column(sa.Numeric(10, 2), nullable=False)
    item_valor_total = sa.Column(sa.Numeric(10, 2), nullable=False)
    extra = sa.Column(sa.JSONB, default={})
    imported_at = pg_timestampz()
    id_nota = sa.Column(sa.BigInteger, sa.ForeignKey("raw.nota.id_nota"))
    id_usuario = sa.Column(sa.BigInteger, sa.ForeignKey("core.usuario.id_usuario"))
