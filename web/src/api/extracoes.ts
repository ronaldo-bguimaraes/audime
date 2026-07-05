import { api } from "./client";

export interface PipelineStep {
  etapa: string;
  status: string;
  ordem: number;
  iniciado_em: string | null;
  concluido_em: string | null;
  mensagem: string | null;
}

export interface ExtracaoResult {
  id_extracao: number;
  status: string;
  created_at: string;
  url?: string;
  empresa?: string | null;
  reprocess_count?: number;
  steps: PipelineStep[];
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

export async function reprocessarExtracao(
  id: number,
  url?: string,
): Promise<{ id_extracao: number; status: string; job_id: string | null }> {
  return api.post(`/v1/extracoes/${id}/reprocessar`, url ? { url } : undefined);
}
