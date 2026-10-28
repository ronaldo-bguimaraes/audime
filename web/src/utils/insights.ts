import type { MesResumoItem } from "../types";

export type InsightTone = "positive" | "negative" | "neutral";

export interface Insight {
  /** Frase curta para o dashboard. */
  text: string;
  tone: InsightTone;
  /** Variação percentual (positiva = gastou mais). */
  delta: number;
}

const MESES = [
  "janeiro",
  "fevereiro",
  "março",
  "abril",
  "maio",
  "junho",
  "julho",
  "agosto",
  "setembro",
  "outubro",
  "novembro",
  "dezembro",
];

function formatPercent(value: number): string {
  return `${Math.round(Math.abs(value) * 100)}%`;
}

function formatMoney(value: number): string {
  return value.toLocaleString("pt-BR", {
    style: "currency",
    currency: "BRL",
    maximumFractionDigits: 0,
  });
}

/**
 * Compara os dois meses mais recentes de `por_mes` e devolve uma frase
 * contextual. Retorna `null` quando não há base de comparação confiável
 * (< 2 meses, ou o mês anterior zerado).
 */
export function computeInsight(porMes: MesResumoItem[]): Insight | null {
  if (!Array.isArray(porMes) || porMes.length < 2) return null;

  const ordenado = [...porMes]
    .filter((m) => Number.isFinite(m.valor))
    .sort((a, b) => a.ano - b.ano || a.mes - b.mes);

  if (ordenado.length < 2) return null;

  const atual = ordenado[ordenado.length - 1];
  const anterior = ordenado[ordenado.length - 2];

  if (anterior.valor <= 0) return null;

  const delta = (atual.valor - anterior.valor) / anterior.valor;
  const mesAnterior = MESES[anterior.mes - 1] ?? "mês anterior";

  if (Math.abs(delta) < 0.005) {
    return {
      text: `Seu gasto em ${MESES[atual.mes - 1] ?? "no mês"} está estável em relação a ${mesAnterior} (${formatMoney(atual.valor)}).`,
      tone: "neutral",
      delta,
    };
  }

  const sentido = delta > 0 ? "a mais" : "a menos";
  const comparativo = delta > 0 ? "que em" : "que em";

  return {
    text: `Você gastou ${formatPercent(delta)} ${sentido} ${comparativo} ${mesAnterior} — ${formatMoney(atual.valor)} no mês.`,
    tone: delta > 0 ? "negative" : "positive",
    delta,
  };
}
