import { api } from "./client";
import type { Nota } from "../types";

export async function listarNotas(): Promise<Nota[]> {
  return api.get<Nota[]>("/v1/notas");
}

export async function obterNota(id: number): Promise<Nota> {
  return api.get<Nota>(`/v1/notas/${id}`);
}
