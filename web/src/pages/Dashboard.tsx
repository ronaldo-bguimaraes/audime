import { Link, useNavigate } from "react-router";
import { useFetch } from "../hooks/useFetch";
import { listarDashboardNotas } from "../api/dashboard";
import { LoadingSpinner } from "../components/LoadingSpinner";
import { ErrorMessage } from "../components/ErrorMessage";
import { formatBRL, maskChave, formatDate } from "../utils/format";
import type { DashboardNota } from "../types";
import styles from "./Dashboard.module.css";

export function Dashboard() {
  const navigate = useNavigate();
  const { data: notas, loading, error, refetch } = useFetch<DashboardNota[]>(
    listarDashboardNotas,
    [],
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
