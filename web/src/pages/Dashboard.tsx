import { Link } from "react-router";
import { FileText } from "lucide-react";
import {
  BarChart,
  Bar,
  XAxis,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
} from "recharts";
import { useFetch } from "../hooks/useFetch";
import { listarDashboardNotas, obterDashboardResumo } from "../api/dashboard";
import { ErrorMessage } from "../components/ErrorMessage";
import { Card, CardHeader } from "../components/ui/Card";
import { Skeleton } from "../components/ui/Skeleton";
import { EmptyState, Stat } from "../components/ui";
import { formatBRL, maskChave, formatDate } from "../utils/format";
import { computeInsight } from "../utils/insights";
import type { DashboardNota, DashboardResumo } from "../types";
import styles from "./Dashboard.module.css";

/* Cores dos gráficos vêm dos tokens — nada de hex aqui. */
const CHART = {
  bar: "var(--accent)",
  axis: "var(--text-muted)",
  grid: "var(--border)",
};

function ChartTooltip({ active, payload, label }: any) {
  if (!active || !payload?.length) return null;
  return (
    <div className={styles.tooltip}>
      <span className={styles.tooltipLabel}>{label}</span>
      <span className={styles.tooltipValue}>{formatBRL(Number(payload[0].value))}</span>
    </div>
  );
}

export function Dashboard() {
  const { data: notas, loading, error, refetch } = useFetch<DashboardNota[]>(
    listarDashboardNotas,
    [],
  );
  const { data: resumo } = useFetch<DashboardResumo>(obterDashboardResumo, []);

  if (error) {
    return <ErrorMessage message={error} onRetry={refetch} />;
  }

  const temResumo = resumo != null && resumo.total_notas > 0;
  const insight = resumo ? computeInsight(resumo.por_mes) : null;
  const maiorEmpresa = resumo?.por_empresa?.[0];
  const maxEmpresa = maiorEmpresa?.valor ?? 1;
  const meses = (resumo?.por_mes ?? []).map((m) => ({
    name: `${String(m.mes).padStart(2, "0")}/${String(m.ano).slice(2)}`,
    valor: m.valor,
  }));

  return (
    <div className={styles.page}>
      <header className={styles.pageHeader}>
        <div>
          <h1>Notas Fiscais</h1>
          <p className={styles.pageSubtitle}>
            Seus gastos extraídos das NFC-e, consolidados por período.
          </p>
        </div>
        <Link to="/extrair" className={styles.primaryLink}>
          Nova extração
        </Link>
      </header>

      {loading && (
        <section className={styles.overview} aria-busy="true">
          <div className={styles.heroRow}>
            <div className={styles.heroBlock}>
              <Skeleton width={120} height={10} />
              <Skeleton width={240} height={40} />
              <Skeleton width={280} height={12} />
            </div>
            <div className={styles.secondaryStats}>
              {[0, 1, 2].map((i) => (
                <div key={i} className={styles.statSkeleton}>
                  <Skeleton width={70} height={10} />
                  <Skeleton width={110} height={20} />
                </div>
              ))}
            </div>
          </div>
        </section>
      )}

      {!loading && temResumo && resumo && (
        <section className={styles.overview}>
          <div className={styles.heroRow}>
            <div className={styles.heroBlock}>
              <span className={styles.heroLabel}>Total no período</span>
              <span className={styles.heroValue}>{formatBRL(resumo.valor_total)}</span>
              {insight && (
                <p
                  className={`${styles.insight} ${styles[`insight_${insight.tone}`]}`}
                  data-tone={insight.tone}
                >
                  {insight.text}
                </p>
              )}
            </div>

            <div className={styles.secondaryStats}>
              <Stat label="Notas" value={resumo.total_notas} hint="no período" />
              <Stat
                label="Média por nota"
                value={formatBRL(resumo.media_por_nota ?? 0)}
                hint="ticket médio"
              />
              <Stat
                label="Maior gasto"
                value={maiorEmpresa ? formatBRL(maiorEmpresa.valor) : "—"}
                hint={maiorEmpresa?.empresa ?? "sem dados"}
              />
            </div>
          </div>

          <div className={styles.supportGrid}>
            <Card>
              <CardHeader title="Gastos por mês" subtitle="Evolução do total extraído" />
              <div className={styles.chartBody}>
                <ResponsiveContainer width="100%" height={180}>
                  <BarChart data={meses} margin={{ top: 4, right: 4, left: 4, bottom: 0 }}>
                    <CartesianGrid vertical={false} stroke={CHART.grid} strokeDasharray="2 4" />
                    <XAxis
                      dataKey="name"
                      tickLine={false}
                      axisLine={false}
                      tick={{ fill: CHART.axis, fontSize: 11 }}
                      dy={6}
                    />
                    <Tooltip cursor={{ fill: "var(--bg-hover)" }} content={<ChartTooltip />} />
                    <Bar dataKey="valor" fill={CHART.bar} radius={[3, 3, 0, 0]} maxBarSize={36} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </Card>

            <Card>
              <CardHeader
                title="Onde você mais gastou"
                subtitle={`${resumo.por_empresa.length} estabelecimentos`}
              />
              <ul className={styles.companyList}>
                {resumo.por_empresa.slice(0, 4).map((empresa) => (
                  <li key={empresa.empresa} className={styles.companyItem}>
                    <div className={styles.companyTop}>
                      <span className={styles.companyName}>{empresa.empresa}</span>
                      <span className={styles.companyValue}>{formatBRL(empresa.valor)}</span>
                    </div>
                    <div className={styles.companyTrack}>
                      <div
                        className={styles.companyBar}
                        style={{ width: `${Math.max(4, (empresa.valor / maxEmpresa) * 100)}%` }}
                      />
                    </div>
                  </li>
                ))}
              </ul>
            </Card>
          </div>
        </section>
      )}

      <section className={styles.listSection}>
        <div className={styles.sectionHeader}>
          <span className={styles.sectionTitle}>Notas</span>
          {notas && notas.length > 0 && (
            <span className={styles.sectionHint}>{notas.length} registros</span>
          )}
        </div>

        {loading ? (
          <div className={styles.rows}>
            {[0, 1, 2].map((i) => (
              <div key={i} className={styles.row}>
                <div className={styles.rowMain}>
                  <Skeleton width={220} height={14} />
                  <Skeleton width={300} height={10} />
                </div>
                <Skeleton width={90} height={18} />
              </div>
            ))}
          </div>
        ) : !notas || notas.length === 0 ? (
          <EmptyState
            icon={<FileText size={18} />}
            title="Nenhuma nota encontrada"
            description="Extraia a primeira NFC-e para começar a acompanhar seus gastos."
            action={
              <Link to="/extrair" className={styles.primaryLink}>
                Nova extração
              </Link>
            }
          />
        ) : (
          <div className={styles.rows}>
            {notas.map((nota) => (
              <article key={nota.id_extracao} className={styles.row}>
                <div className={styles.rowMain}>
                  <h2 className={styles.empresa}>{nota.empresa}</h2>
                  <span className={styles.meta}>
                    #{nota.id_extracao}
                    {nota.chave_acesso ? ` · ${maskChave(nota.chave_acesso)}` : ""}
                    {nota.emissao ? ` · ${formatDate(nota.emissao)}` : ""}
                  </span>
                </div>
                <div className={styles.rowNumbers}>
                  <span className={styles.items}>{nota.items.length} itens</span>
                  <span className={styles.valor}>{formatBRL(nota.valor_total ?? 0)}</span>
                </div>
                <Link to={`/notas/${nota.id_extracao}`} className={styles.detailsLink}>
                  Ver detalhes
                </Link>
              </article>
            ))}
          </div>
        )}
      </section>
    </div>
  );
}
