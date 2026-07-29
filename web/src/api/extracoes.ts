import { api } from "./client";

import type {
  CriarExtracaoResult,
  ExtracaoResult,
  PipelineStep,
} from "shared";

export type { CriarExtracaoResult, ExtracaoResult, PipelineStep };

export async function criarExtracao(url: string): Promise<CriarExtracaoResult> {
  return api.post<CriarExtracaoResult>("/v1/extracoes", { url, tipo: "NFCE" });
}

export async function listarExtracoes(limit = 10): Promise<ExtracaoResult[]> {
  return api.get<ExtracaoResult[]>(`/v1/extracoes?limit=${limit}`);
}

export async function reprocessarExtracao(
  id: number,
  url?: string,
): Promise<CriarExtracaoResult> {
  return api.post(`/v1/extracoes/${id}/reprocessar`, url ? { url } : undefined);
}
