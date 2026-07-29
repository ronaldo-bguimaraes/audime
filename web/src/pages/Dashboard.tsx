import { Link, useNavigate } from "react-router";
import { useFetch } from "../hooks/useFetch";
import { listarDashboardNotas, obterDashboardResumo } from "../api/dashboard";
import { LoadingSpinner } from "../components/LoadingSpinner";
import { ErrorMessage } from "../components/ErrorMessage";
import { formatBRL, maskChave, formatDate } from "../utils/format";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, PieChart, Pie, Cell, Legend } from "recharts";
import type { DashboardNota, DashboardResumo } from "../types";
import styles from "./Dashboard.module.css";

const PIE_COLORS = ["#6366f1", "#8b5cf6", "#a78bfa", "#c4b5fd", "#ddd6fe"];

export function Dashboard() {
  const navigate = useNavigate();
  const { data: notas, loading, error, refetch } = useFetch<DashboardNota[]>(
    listarDashboardNotas,
    [],
  );
  const { data: resumo } = useFetch<DashboardResumo>(
    obterDashboardResumo,
    null,
  );

  if (loading) {
    return <LoadingSpinner message="Carregando notas..." />;
  }

  if (error) {
    return <ErrorMessage message={error} onRetry={refetch} />;
  }

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <h1 className={styles.title}>Notas Fiscais</h1>
        <Link to="/extrair" className={styles.newButton}>
          + Nova Extração
        </Link>
      </div>

      {resumo && resumo.total_notas > 0 && (
        <section className={styles.resumoSection}>
          <h2 className={styles.sectionTitle}>Resumo Financeiro</h2>

          {/* Summary cards */}
          <div className={styles.summaryCards}>
            <div className={styles.summaryCard}>
              <span className={styles.summaryLabel}>Total de Notas</span>
              <span className={styles.summaryValue}>{resumo.total_notas}</span>
            </div>
            <div className={styles.summaryCard}>
              <span className={styles.summaryLabel}>Valor Total</span>
              <span className={styles.summaryValue}>{formatBRL(resumo.valor_total)}</span>
            </div>
            <div className={styles.summaryCard}>
              <span className={styles.summaryLabel}>Média por Nota</span>
              <span className={styles.summaryValue}>{formatBRL(resumo.media_por_nota ?? 0)}</span>
            </div>
          </div>

          {/* Charts row */}
          <div className={styles.chartsRow}>
            {/* Monthly bar chart */}
            {resumo.por_mes.length > 0 && (
              <div className={styles.chartBox}>
                <h3 className={styles.chartTitle}>Gastos por Mês</h3>
                <ResponsiveContainer width="100%" height={220}>
                  <BarChart data={resumo.por_mes.map((m) => ({
                    name: `${String(m.mes).padStart(2, "0")}/${m.ano}`,
                    valor: m.valor,
                  }))}>
                    <XAxis dataKey="name" fontSize={11} />
                    <YAxis fontSize={11} tickFormatter={(v: number) => `R$${v}`} />
                    <Tooltip formatter={(value: number) => formatBRL(value)} />
                    <Bar dataKey="valor" fill="#6366f1" radius={[4, 4, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            )}

            {/* Per-company pie chart */}
            {resumo.por_empresa.length > 0 && (
              <div className={styles.chartBox}>
                <h3 className={styles.chartTitle}>Gastos por Empresa</h3>
                <ResponsiveContainer width="100%" height={220}>
                  <PieChart>
                    <Pie
                      data={resumo.por_empresa}
                      dataKey="valor"
                      nameKey="empresa"
                      cx="50%"
                      cy="50%"
                      outerRadius={80}
                      label={({ empresa, percent }: { empresa: string; percent: number }) =>
                        `${empresa.substring(0, 12)}… ${(percent * 100).toFixed(0)}%`
                      }
                    >
                      {resumo.por_empresa.map((_, idx) => (
                        <Cell key={idx} fill={PIE_COLORS[idx % PIE_COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip formatter={(value: number) => formatBRL(value)} />
                  </PieChart>
                </ResponsiveContainer>
              </div>
            )}
          </div>
        </section>
      )}

      {!notas || notas.length === 0 ? (
        <div className={styles.empty}>
          <div className={styles.emptyIcon}>
            <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
              <polyline points="14 2 14 8 20 8" />
              <line x1="16" y1="13" x2="8" y2="13" />
              <line x1="16" y1="17" x2="8" y2="17" />
              <polyline points="10 9 9 9 8 9" />
            </svg>
          </div>
          <p>Nenhuma nota fiscal encontrada.</p>
          <p>
            Faça uma{" "}
            <Link to="/extrair" className={styles.emptyLink}>
              nova extração
            </Link>{" "}
            para começar.
          </p>
        </div>
      ) : (
        <div className={styles.grid}>
          {notas.map((nota) => (
            <NotaCard key={nota.id_extracao} nota={nota} navigate={navigate} />
          ))}
        </div>
      )}
    </div>
  );
}

function NotaCard({ nota, navigate }: { nota: DashboardNota; navigate: ReturnType<typeof useNavigate> }) {
  return (
    <div
      className={styles.card}
      role="button"
      tabIndex={0}
      onClick={() => navigate(`/notas/${nota.id_extracao}`)}
      onKeyDown={(ev) => {
        if (ev.key === "Enter" || ev.key === " ") {
          ev.preventDefault();
          navigate(`/notas/${nota.id_extracao}`);
        }
      }}
    >
      <div className={styles.cardHeader}>
        <h2 className={styles.empresa}>#{nota.id_extracao} {nota.empresa}</h2>
        <span className={styles.valor}>{formatBRL(nota.valor_total ?? 0)}</span>
      </div>
      <div className={styles.cardBody}>
        <div className={styles.info}>
          <span className={styles.label}>Chave:</span>
          <span className={styles.value}>{maskChave(nota.chave_acesso ?? "")}</span>
        </div>
        <div className={styles.info}>
          <span className={styles.label}>Emissão:</span>
          <span className={styles.value}>{nota.emissao ? formatDate(nota.emissao) : "-"}</span>
        </div>
        <div className={styles.info}>
          <span className={styles.label}>Itens:</span>
          <span className={styles.value}>{nota.items.length}</span>
        </div>
      </div>
    </div>
  );
}
