import { api } from "./client";

export interface ExtracaoResult {
  id_extracao: number;
  status: string;
  created_at: string;
}

export interface CriarExtracaoResult {
  id_extracao: number;
  status: string;
  job_id: string | null;
}

export async function criarExtracao(url: string): Promise<CriarExtracaoResult> {
  return api.post<CriarExtracaoResult>("/v1/extracoes", {
    url,
    tipo: "NFCE",
  });
}

export async function listarExtracoes(limit = 10): Promise<ExtracaoResult[]> {
  return api.get<ExtracaoResult[]>(`/v1/extracoes?limit=${limit}`);
}
