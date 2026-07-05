import { useParams, useNavigate } from "react-router";
import { useFetch } from "../hooks/useFetch";
import { obterDashboardNota, obterHistoricoNota } from "../api/dashboard";
import { LoadingSpinner } from "../components/LoadingSpinner";
import { ErrorMessage } from "../components/ErrorMessage";
import { formatBRL, formatDate } from "../utils/format";
import type { DashboardNota, VersaoNota } from "../types";
import styles from "./NotaDetalhe.module.css";

export function NotaDetalhe() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const idExtracao = Number(id);

  const {
    data: nota,
    loading,
    error,
    refetch,
  } = useFetch<DashboardNota>(
    () => obterDashboardNota(idExtracao),
    [idExtracao],
  );

  const { data: versoes } = useFetch<VersaoNota[]>(
    () => obterHistoricoNota(idExtracao),
    [idExtracao],
  );

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
          <InfoRow label="Chave" value={nota.chave_acesso ?? "-"} />
          <InfoRow label="Número" value={nota.numero ?? "-"} />
          <InfoRow label="Série" value={nota.serie ?? "-"} />
          <InfoRow label="Emissão" value={nota.emissao ? formatDate(nota.emissao) : "-"} />
          <InfoRow
            label="Valor Total"
            value={formatBRL(nota.valor_total ?? 0)}
          />
          {nota.qtd_total_itens != null && (
            <InfoRow label="Qtd. Itens" value={String(nota.qtd_total_itens)} />
          )}
          <InfoRow label="Versão" value={`v${nota.version}`} />
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
                {nota.items.map((item, idx) => (
                  <tr key={idx}>
                    <td data-label="Descrição">{item.descricao}</td>
                    <td data-label="Qtd">{item.quantidade ?? "-"}</td>
                    <td data-label="Un.">
                      {item.unidade ?? "-"}
                    </td>
                    <td data-label="Valor Un.">
                      {item.valor_unitario != null ? formatBRL(item.valor_unitario) : "-"}
                    </td>
                    <td data-label="Valor Total">
                      {item.valor_total != null ? formatBRL(item.valor_total) : "-"}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {versoes && versoes.length > 1 && (
        <HistoricoVersoes versoes={versoes} />
      )}
    </div>
  );
}

function HistoricoVersoes({ versoes }: { versoes: VersaoNota[] }) {
  return (
    <div className={styles.historicoCard}>
      <h2 className={styles.sectionTitle}>
        Histórico de Versões ({versoes.length})
      </h2>
      <div className={styles.historicoList}>
        {versoes.map((v) => (
          <div
            key={v.version}
            className={styles.historicoItem}
            style={{ borderLeft: v.is_current ? "3px solid var(--accent)" : "3px solid var(--border)" }}
          >
            <InfoRow
              label={`Versão ${v.version}`}
              value={v.is_current ? "Atual" : "Anterior"}
            />
            <InfoRow label="Empresa" value={v.empresa ?? "-"} />
            <InfoRow label="Valor" value={formatBRL(v.valor_total ?? 0)} />
            <InfoRow label="De" value={new Date(v.valid_from).toLocaleString("pt-BR")} />
            {v.valid_to && (
              <InfoRow label="Até" value={new Date(v.valid_to).toLocaleString("pt-BR")} />
            )}
          </div>
        ))}
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
