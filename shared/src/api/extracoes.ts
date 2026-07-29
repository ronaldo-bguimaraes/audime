import type { ApiClient } from "./client";

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

export function createExtracoesApi(api: ApiClient) {
  return {
    criar: (url: string): Promise<CriarExtracaoResult> =>
      api.post<CriarExtracaoResult>("/v1/extracoes", { url, tipo: "NFCE" }),

    listar: (limit = 10): Promise<ExtracaoResult[]> =>
      api.get<ExtracaoResult[]>(`/v1/extracoes?limit=${limit}`),

    reprocessar: (id: number, url?: string): Promise<CriarExtracaoResult> =>
      api.post(`/v1/extracoes/${id}/reprocessar`, url ? { url } : undefined),
  };
}

export type ExtracoesApi = ReturnType<typeof createExtracoesApi>;
