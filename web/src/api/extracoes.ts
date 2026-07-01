import { api } from "./client";

export interface ExtracaoResult {
  data?: {
    id_extracao: number;
    status: string;
    created_at: string;
  };
  id_extracao?: number;
  status?: string;
}

export async function criarExtracao(url: string): Promise<ExtracaoResult> {
  return api.post<ExtracaoResult>("/v1/extracoes", {
    url,
    tipo: "NFCE",
  });
}
