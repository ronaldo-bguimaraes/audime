import type { ApiClient } from "./client";
import type { Nota } from "../types";

export function createNotasApi(api: ApiClient) {
  return {
    listar: (): Promise<Nota[]> => api.get<Nota[]>("/v1/notas"),

    obter: (id: number): Promise<Nota> => api.get<Nota>(`/v1/notas/${id}`),
  };
}

export type NotasApi = ReturnType<typeof createNotasApi>;
