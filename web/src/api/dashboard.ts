import { api } from "./client";
import type { DashboardNota, VersaoNota } from "../types";

export async function listarDashboardNotas(): Promise<DashboardNota[]> {
  return api.get<DashboardNota[]>("/v1/dashboard/notas");
}

export async function obterDashboardNota(idExtracao: number): Promise<DashboardNota> {
  return api.get<DashboardNota>(`/v1/dashboard/notas/${idExtracao}`);
}

export async function obterHistoricoNota(idExtracao: number): Promise<VersaoNota[]> {
  return api.get<VersaoNota[]>(`/v1/dashboard/notas/${idExtracao}/historico`);
}
