import type { ApiClient } from "./client";
import type { Nota } from "../types";

export function createNotasApi(api: ApiClient) {
  return {
    listar: (): Promise<Nota[]> => api.get<Nota[]>("/v1/notas"),

    listarPorExtracao: (extracaoId: number): Promise<Nota[]> =>
      api.get<Nota[]>(`/v1/notas?extracao_id=${extracaoId}`),

    obter: (id: number): Promise<Nota> => api.get<Nota>(`/v1/notas/${id}`),
  };
}

export type NotasApi = ReturnType<typeof createNotasApi>;
