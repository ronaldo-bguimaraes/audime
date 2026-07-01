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

export interface Nota {
  id: number;
  empresa: string;
  chave: string;
  numero: string;
  serie: string;
  emissao: string;
  valor_total: number;
  items: ItemNota[];
}

/* ---- Analytics ---- */

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
