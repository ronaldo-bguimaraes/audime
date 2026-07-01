import { Link } from "react-router";
import { useFetch } from "../hooks/useFetch";
import { listarNotas } from "../api/notas";
import { LoadingSpinner } from "../components/LoadingSpinner";
import { ErrorMessage } from "../components/ErrorMessage";
import { formatBRL, maskChave, formatDate } from "../utils/format";
import type { Nota } from "../types";
import styles from "./Dashboard.module.css";

export function Dashboard() {
  const { data: notas, loading, error, refetch } = useFetch<Nota[]>(
    listarNotas,
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
            <NotaCard key={nota.id} nota={nota} />
          ))}
        </div>
      )}
    </div>
  );
}

function NotaCard({ nota }: { nota: Nota }) {
  return (
    <div className={styles.card}>
      <div className={styles.cardHeader}>
        <h2 className={styles.empresa}>{nota.empresa}</h2>
        <span className={styles.valor}>{formatBRL(nota.valor_total)}</span>
      </div>
      <div className={styles.cardBody}>
        <div className={styles.info}>
          <span className={styles.label}>Chave:</span>
          <span className={styles.value}>{maskChave(nota.chave)}</span>
        </div>
        <div className={styles.info}>
          <span className={styles.label}>Emissão:</span>
          <span className={styles.value}>{formatDate(nota.emissao)}</span>
        </div>
        <div className={styles.info}>
          <span className={styles.label}>Itens:</span>
          <span className={styles.value}>{nota.items.length}</span>
        </div>
      </div>
      <Link to={`/notas/${nota.id}`} className={styles.detailsButton}>
        Ver detalhes
      </Link>
    </div>
  );
}
