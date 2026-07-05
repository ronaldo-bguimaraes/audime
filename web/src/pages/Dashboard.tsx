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
          <p>Nenhuma nota encontrada.</p>
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
