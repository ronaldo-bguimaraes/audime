from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, HttpUrl


class ExtracaoRequest(BaseModel):
    url: HttpUrl
    tipo: str = "NFCE"


class ExtracaoJobResponse(BaseModel):
    """Response returned immediately after enqueuing an extraction job."""

    id_extracao: int
    status: str = "PENDING"
    job_id: str | None = None
    url: Optional[str] = None


class ExtracaoStatusResponse(BaseModel):
    """Status of an extraction (for polling)."""

    id_extracao: int
    status: str
    url: Optional[str] = None


class ExtracaoResponse(BaseModel):
    id_extracao: int
    status: str
    created_at: datetime
    url: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class ItemResponse(BaseModel):
    id: int
    item_codigo: Optional[str]
    item_descricao: str
    item_quantidade: float
    item_tipo_unidade: Optional[str]
    item_valor_unidade: float
    item_valor_total: float
    nota_id: int

    model_config = ConfigDict(from_attributes=True)


class NotaResponse(BaseModel):
    id: int
    empresa: str
    chave: str
    numero: str
    serie: str
    emissao: date
    valor_total: float
    qtd_total_itens: Optional[int] = None
    extra: Optional[dict] = None
    items: list[ItemResponse]

    model_config = ConfigDict(from_attributes=True)


class FaturaRequest(BaseModel):
    url: Optional[str] = None
    banco: str
    nome_titular: str


class FaturaResponse(BaseModel):
    id_fatura: int
    banco: str
    nome_titular: str
    mes_referencia: Optional[date]
    imported_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TransacaoResponse(BaseModel):
    id_transacao: int
    data_realizacao: date
    descricao: Optional[str]
    valor: float
    final_cartao: Optional[str]
    parcela: Optional[str]

    model_config = ConfigDict(from_attributes=True)


class VincularFaturaRequest(BaseModel):
    id_fatura: int


class GastoMensalResponse(BaseModel):
    mes_ano: date
    total_gasto: float
    qtd_transacoes: int
    qtd_notas: int


class GastoCategoriaResponse(BaseModel):
    categoria: str
    mes_ano: date
    total_gasto: float
    qtd_itens: int
