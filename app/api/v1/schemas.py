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
    reprocess_count: Optional[int] = None
    reprocessed_at: Optional[datetime] = None


class ParsingAttemptItem(BaseModel):
    descricao: str
    quantidade: Optional[float] = None
    unidade: Optional[str] = None
    valor_total: Optional[float] = None


class ParsingAttemptResponse(BaseModel):
    id_importacao: int
    id_nota: Optional[int] = None
    imported_at: datetime
    empresa: Optional[str] = None
    chave: Optional[str] = None
    numero: Optional[str] = None
    serie: Optional[str] = None
    emissao: Optional[date] = None
    valor_total: Optional[float] = None
    qtd_total_itens: Optional[int] = None
    items: list[ParsingAttemptItem] = []


class PipelineStepResponse(BaseModel):
    etapa: str
    status: str
    ordem: int
    iniciado_em: Optional[datetime] = None
    concluido_em: Optional[datetime] = None
    mensagem: Optional[str] = None


class ExtracaoResponse(BaseModel):
    id_extracao: int
    status: str
    created_at: datetime
    url: Optional[str] = None
    empresa: Optional[str] = None
    reprocess_count: Optional[int] = None
    reprocessed_at: Optional[datetime] = None
    historico_parsing: list[ParsingAttemptResponse] = []
    steps: list[PipelineStepResponse] = []

    model_config = ConfigDict(from_attributes=True)


class ReprocessarExtracaoRequest(BaseModel):
    url: Optional[HttpUrl] = None


class ReprocessarExtracaoResponse(BaseModel):
    id_extracao: int
    status: str
    job_id: str | None = None


class BackfillResponse(BaseModel):
    enqueued: int
    total: int
    message: str


class ItemResponse(BaseModel):
    id: int
    item_codigo: Optional[str]
    item_descricao: str
    item_quantidade: float
    item_tipo_unidade: Optional[str]
    item_valor_unidade: float | None
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


class DashboardNotaItem(BaseModel):
    descricao: str
    quantidade: Optional[float] = None
    unidade: Optional[str] = None
    valor_unitario: Optional[float] = None
    valor_total: Optional[float] = None


class DashboardNotaResponse(BaseModel):
    id_nota_analytics: int
    id_extracao: int
    empresa: Optional[str] = None
    chave_acesso: Optional[str] = None
    numero: Optional[str] = None
    serie: Optional[str] = None
    emissao: Optional[date] = None
    valor_total: Optional[float] = None
    qtd_total_itens: Optional[int] = None
    valid_from: datetime
    items: list[DashboardNotaItem] = []

    model_config = ConfigDict(from_attributes=True)


class VersaoNotaResponse(BaseModel):
    valid_from: datetime
    valid_to: Optional[datetime] = None
    is_current: bool
    empresa: Optional[str] = None
    valor_total: Optional[float] = None


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
