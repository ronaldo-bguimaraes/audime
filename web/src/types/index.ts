/* ---- Autenticação ---- */

export interface AuthState {
  token: string | null;
  idUsuario: number | null;
  nome: string | null;
  email: string | null;
}

export interface CodeRequest {
  email: string;
}

export interface CodeResponse {
  status: string;
}

export interface VerifyRequest {
  email: string;
  code: string;
}

export interface VerifyResponse {
  status: string;
  access_token?: string;
  id_usuario?: number;
}

export interface MeResponse {
  id_usuario: number;
  nome: string;
  email: string;
}

/* ---- Extração ---- */

export interface ExtracaoRequest {
  url: string;
  tipo: string;
}

export interface ExtracaoResponse {
  id_extracao: number;
  status: string;
  created_at: string;
}

export interface PipelineStep {
  etapa: string;
  status: string;
  ordem: number;
  iniciado_em: string | null;
  concluido_em: string | null;
  mensagem: string | null;
}

/* ---- Notas Fiscais ---- */

export interface ItemNota {
  id: number;
  item_codigo: string | null;
  item_descricao: string;
  item_quantidade: number;
  item_tipo_unidade: string | null;
  item_valor_unidade: number;
  item_valor_total: number;
  nota_id: number;
}

export interface Emitente {
  cnpj: string;
  logradouro: string;
  numero: string;
  complemento: string | null;
  bairro: string;
  cidade: string;
  uf: string;
}

export interface ProtocoloAutorizacao {
  numero: string;
  data_hora: string;
}

export interface FormaPagamento {
  tipo: string;
  valor: number | null;
}

export interface InformacoesInteresse {
  tributos_federal: number | null;
  tributos_estadual: number | null;
  tributos_municipal: number | null;
  coo: number | null;
  pdv: number | null;
}

export interface NotaExtra {
  emitente?: Emitente;
  protocolo_autorizacao?: ProtocoloAutorizacao;
  formas_pagamento?: FormaPagamento[];
  informacoes_interesse?: InformacoesInteresse;
  consumidor?: string;
  ambiente?: string;
}

export interface Nota {
  id: number;
  empresa: string;
  chave: string;
  numero: string;
  serie: string;
  emissao: string;
  valor_total: number;
  qtd_total_itens: number | null;
  extra: NotaExtra | null;
  items: ItemNota[];
}

/* ---- Analytics / Dashboard ---- */

export interface DashboardNotaItem {
  descricao: string;
  quantidade: number | null;
  unidade: string | null;
  valor_unitario: number | null;
  valor_total: number | null;
}

export interface DashboardNota {
  id_nota_analytics: number;
  id_extracao: number;
  empresa: string | null;
  chave_acesso: string | null;
  numero: string | null;
  serie: string | null;
  emissao: string | null;
  valor_total: number | null;
  qtd_total_itens: number | null;
  valid_from: string;
  items: DashboardNotaItem[];
}

export interface VersaoNota {
  valid_from: string;
  valid_to: string | null;
  is_current: boolean;
  empresa: string | null;
  valor_total: number | null;
}

export interface GastoMensal {
  mes_ano: string;
  total_gasto: number;
  qtd_transacoes: number;
  qtd_notas: number;
}

export interface GastoCategoria {
  categoria: string;
  mes_ano: string;
  total_gasto: number;
  qtd_itens: number;
}

/* ---- Genérico ---- */

export interface ApiError {
  message: string;
  status?: number;
}
