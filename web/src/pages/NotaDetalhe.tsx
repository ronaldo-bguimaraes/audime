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
          {nota.qtd_total_itens != null && (
            <InfoRow label="Qtd. Itens" value={String(nota.qtd_total_itens)} />
          )}
          {nota.extra?.emitente?.cnpj && (
            <InfoRow label="CNPJ" value={nota.extra.emitente.cnpj} />
          )}
          {nota.extra?.emitente?.logradouro && (
            <InfoRow
              label="Endereço"
              value={`${nota.extra.emitente.logradouro}, ${nota.extra.emitente.numero}${nota.extra.emitente.complemento ? ` - ${nota.extra.emitente.complemento}` : ""} - ${nota.extra.emitente.bairro}, ${nota.extra.emitente.cidade}/${nota.extra.emitente.uf}`}
            />
          )}
          {nota.extra?.protocolo_autorizacao?.numero && (
            <InfoRow
              label="Protocolo"
              value={`${nota.extra.protocolo_autorizacao.numero} (${nota.extra.protocolo_autorizacao.data_hora})`}
            />
          )}
          {nota.extra?.consumidor && (
            <InfoRow label="Consumidor" value={nota.extra.consumidor} />
          )}
          {nota.extra?.ambiente && (
            <InfoRow label="Ambiente" value={nota.extra.ambiente} />
          )}
        </div>
      </div>

      <div className={styles.itensSection}>
        <h2 className={styles.itensTitle}>
          Itens ({nota.qtd_total_itens ?? nota.items.length})
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
      {/* ── Formas de Pagamento ── */}
      {nota.extra?.formas_pagamento && nota.extra.formas_pagamento.length > 0 && (
        <div className={styles.card}>
          <h2 className={styles.sectionTitle}>Formas de Pagamento</h2>
          <div className={styles.infoGrid}>
            {nota.extra.formas_pagamento.map((fp, idx) => (
              <InfoRow
                key={idx}
                label={fp.tipo}
                value={fp.valor != null ? formatBRL(fp.valor) : "—"}
              />
            ))}
          </div>
        </div>
      )}

      {/* ── Informações de Interesse ── */}
      {nota.extra?.informacoes_interesse && (
        <div className={styles.card}>
          <h2 className={styles.sectionTitle}>Informações de Interesse</h2>
          <div className={styles.infoGrid}>
            {nota.extra.informacoes_interesse.tributos_federal != null && (
              <InfoRow label="Trib. Federal" value={formatBRL(nota.extra.informacoes_interesse.tributos_federal)} />
            )}
            {nota.extra.informacoes_interesse.tributos_estadual != null && (
              <InfoRow label="Trib. Estadual" value={formatBRL(nota.extra.informacoes_interesse.tributos_estadual)} />
            )}
            {nota.extra.informacoes_interesse.tributos_municipal != null && (
              <InfoRow label="Trib. Municipal" value={formatBRL(nota.extra.informacoes_interesse.tributos_municipal)} />
            )}
            {nota.extra.informacoes_interesse.coo != null && (
              <InfoRow label="COO" value={String(nota.extra.informacoes_interesse.coo)} />
            )}
            {nota.extra.informacoes_interesse.pdv != null && (
              <InfoRow label="PDV" value={String(nota.extra.informacoes_interesse.pdv)} />
            )}
          </div>
        </div>
      )}
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
