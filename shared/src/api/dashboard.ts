import type { ApiClient } from "./client";
import type { DashboardNota, DashboardResumo, VersaoNota } from "../types";

export function createDashboardApi(api: ApiClient) {
  return {
    listarNotas: (): Promise<DashboardNota[]> =>
      api.get<DashboardNota[]>("/v1/dashboard/notas"),

    obterResumo: (): Promise<DashboardResumo> =>
      api.get<DashboardResumo>("/v1/dashboard/resumo"),

    obterNota: (idExtracao: number): Promise<DashboardNota> =>
      api.get<DashboardNota>(`/v1/dashboard/notas/${idExtracao}`),

    obterHistorico: (idExtracao: number): Promise<VersaoNota[]> =>
      api.get<VersaoNota[]>(`/v1/dashboard/notas/${idExtracao}/historico`),

    desativar: (idExtracao: number, isActive: boolean): Promise<{ status: string }> =>
      api.patch<{ status: string }>(`/v1/dashboard/notas/${idExtracao}`, { is_active: isActive }),
  };
}

export type DashboardApi = ReturnType<typeof createDashboardApi>;
