import { useState, useEffect, useCallback, type FormEvent } from "react";
import { criarExtracao, listarExtracoes, type ExtracaoResult } from "../api/extracoes";
import { FetchError } from "../api/client";
import styles from "./Extrair.module.css";

const STATUS_ATIVOS = new Set(["PENDING", "RUNNING"]);

function StatusBadge({ status }: { status: string }) {
  const className = `${styles.badge} ${styles[`badge_${status.toLowerCase()}`] || ""}`;
  const animated = status === "RUNNING" ? styles.pulse : "";
  return <span className={`${className} ${animated}`}>{status}</span>;
}

export function Extrair() {
  const [url, setUrl] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [extracoes, setExtracoes] = useState<ExtracaoResult[]>([]);
  const [polling, setPolling] = useState(false);
  const [modalExtracao, setModalExtracao] = useState<ExtracaoResult | null>(null);

  const fetchExtracoes = useCallback(async () => {
    try {
      const data = await listarExtracoes(10);
      setExtracoes(data);
      const hasAtivas = data.some((e) => STATUS_ATIVOS.has(e.status));
      setPolling(hasAtivas);
    } catch {
      setPolling(false);
    }
  }, []);

  useEffect(() => {
    fetchExtracoes();
  }, [fetchExtracoes]);

  useEffect(() => {
    if (!polling) return;
    const id = setInterval(fetchExtracoes, 5000);
    return () => clearInterval(id);
  }, [polling, fetchExtracoes]);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError(null);
    setSuccess(null);
    setLoading(true);

    try {
      await criarExtracao(url);
      setUrl("");
      setSuccess("Extração iniciada com sucesso!");
      await fetchExtracoes();
    } catch (err) {
      const message =
        err instanceof FetchError
          ? err.message
          : "Erro ao iniciar extração";
      setError(message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className={styles.container}>
      <div className={styles.card}>
        <h1 className={styles.title}>Nova Extração</h1>
        <p className={styles.description}>
          Cole a URL do QR Code da NFC-e para extrair os dados da nota fiscal.
        </p>

        {error && (
          <div className={styles.error} role="alert">
            {error}
          </div>
        )}

        {success && (
          <div className={styles.success} role="status">
            {success}
          </div>
        )}

        <form onSubmit={handleSubmit} className={styles.form}>
          <label htmlFor="extracao-url" className={styles.label}>
            URL do QR Code NFC-e
          </label>
          <input
            id="extracao-url"
            type="url"
            required
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            placeholder="https://www.sefaz.mt.gov.br/nfce/consultanfce?p=..."
            className={styles.input}
            disabled={loading}
          />
          <button
            type="submit"
            className={styles.button}
            disabled={loading || !url}
          >
            {loading ? "Extraindo..." : "Extrair"}
          </button>
        </form>
      </div>

      <div className={styles.listCard}>
        <h2 className={styles.listTitle}>Extrações Recentes</h2>
        {extracoes.length === 0 ? (
          <p className={styles.empty}>Nenhuma extração encontrada.</p>
        ) : (
          <div className={styles.table}>
            <div className={styles.tableHeader}>
              <span className={styles.colId}>#</span>
              <span className={styles.colData}>Data</span>
              <span className={styles.colStatus}>Status</span>
            </div>
            {extracoes.map((e) => (
              <div
                key={e.id_extracao}
                className={styles.tableRow}
                onClick={() => setModalExtracao(e)}
                role="button"
                tabIndex={0}
                onKeyDown={(ev) => {
                  if (ev.key === "Enter" || ev.key === " ") {
                    ev.preventDefault();
                    setModalExtracao(e);
                  }
                }}
              >
                <span className={styles.colId}>{e.id_extracao}</span>
                <span className={styles.colData}>
                  {new Date(e.created_at).toLocaleString("pt-BR")}
                </span>
                <span className={styles.colStatus}>
                  <StatusBadge status={e.status} />
                </span>
              </div>
            ))}
          </div>
        )}
      </div>

      {modalExtracao && (
        <div
          className={styles.modalOverlay}
          onClick={() => setModalExtracao(null)}
          role="dialog"
          aria-modal="true"
        >
          <div
            className={styles.modal}
            onClick={(e) => e.stopPropagation()}
          >
            <button
              className={styles.modalClose}
              onClick={() => setModalExtracao(null)}
              aria-label="Fechar"
            >
              &times;
            </button>
            <h3 className={styles.modalTitle}>
              Extração #{modalExtracao.id_extracao}
            </h3>
            <dl className={styles.modalDetails}>
              <dt>Status</dt>
              <dd>
                <StatusBadge status={modalExtracao.status} />
              </dd>
              <dt>Data</dt>
              <dd>
                {new Date(modalExtracao.created_at).toLocaleString("pt-BR")}
              </dd>
              {modalExtracao.url && (
                <>
                  <dt>URL</dt>
                  <dd>
                    <a
                      href={modalExtracao.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className={styles.modalUrl}
                    >
                      {modalExtracao.url}
                    </a>
                  </dd>
                </>
              )}
            </dl>
          </div>
        </div>
      )}
    </div>
  );
}