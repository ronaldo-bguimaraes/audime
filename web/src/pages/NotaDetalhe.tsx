import { useParams, useNavigate } from "react-router";
import { useFetch } from "../hooks/useFetch";
import { obterNota } from "../api/notas";
import { LoadingSpinner } from "../components/LoadingSpinner";
import { ErrorMessage } from "../components/ErrorMessage";
import { formatBRL, formatDate } from "../utils/format";
import type { Nota } from "../types";
import styles from "./NotaDetalhe.module.css";

export function NotaDetalhe() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const notaId = Number(id);

  const {
    data: nota,
    loading,
    error,
    refetch,
  } = useFetch<Nota>(() => obterNota(notaId), [notaId]);

  if (loading) {
    return <LoadingSpinner message="Carregando nota..." />;
  }

  if (error) {
    return (
      <ErrorMessage
        message={error.includes("404") ? "Nota não encontrada" : error}
        onRetry={refetch}
      />
    );
  }

  if (!nota) {
    return <ErrorMessage message="Nota não encontrada" />;
  }

  return (
    <div className={styles.container}>
      <button
        type="button"
        className={styles.backButton}
        onClick={() => navigate("/dashboard")}
      >
        ← Voltar
      </button>

      <div className={styles.card}>
        <h1 className={styles.empresa}>{nota.empresa}</h1>
        <div className={styles.infoGrid}>
          <InfoRow label="Chave" value={nota.chave} />
          <InfoRow label="Número" value={nota.numero} />
          <InfoRow label="Série" value={nota.serie} />
          <InfoRow label="Emissão" value={formatDate(nota.emissao)} />
          <InfoRow
            label="Valor Total"
            value={formatBRL(nota.valor_total)}
          />
        </div>
      </div>

      <div className={styles.itensSection}>
        <h2 className={styles.itensTitle}>
          Itens ({nota.items.length})
        </h2>
        {nota.items.length === 0 ? (
          <p className={styles.noItens}>Nenhum item encontrado.</p>
        ) : (
          <div className={styles.tableWrapper}>
            <table className={styles.table}>
              <thead>
                <tr>
                  <th>Descrição</th>
                  <th>Qtd</th>
                  <th>Un.</th>
                  <th>Valor Un.</th>
                  <th>Valor Total</th>
                </tr>
              </thead>
              <tbody>
                {nota.items.map((item) => (
                  <tr key={item.id}>
                    <td data-label="Descrição">{item.item_descricao}</td>
                    <td data-label="Qtd">{item.item_quantidade}</td>
                    <td data-label="Un.">
                      {item.item_tipo_unidade ?? "-"}
                    </td>
                    <td data-label="Valor Un.">
                      {formatBRL(item.item_valor_unidade)}
                    </td>
                    <td data-label="Valor Total">
                      {formatBRL(item.item_valor_total)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}

function InfoRow({ label, value }: { label: string; value: string }) {
  return (
    <div className={styles.infoRow}>
      <span className={styles.infoLabel}>{label}:</span>
      <span className={styles.infoValue}>{value}</span>
    </div>
  );
}
