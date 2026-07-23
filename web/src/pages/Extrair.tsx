import { useState, useEffect, useCallback, type FormEvent } from "react";
import { useNavigate } from "react-router";
import { criarExtracao, listarExtracoes, reprocessarExtracao, type ExtracaoResult, type PipelineStep } from "../api/extracoes";
import { FetchError } from "../api/client";
import { QrCodeScanner } from "../components/QrCodeScanner";
import styles from "./Extrair.module.css";

const STATUS_ATIVOS = new Set(["PENDING", "RUNNING"]);

const STEP_ORDER: Record<string, number> = {
  RAW_IMPORT: 1,
  STAGING: 2,
  ANALYTICS: 3,
  COMPLETE: 4,
};

const STEP_STATUS_ORDER: Record<string, number> = {
  ERROR: 0,
  RUNNING: 1,
  DONE: 2,
  PENDING: 3,
};

function latestStep(steps: PipelineStep[]): string | null {
  if (!steps.length) return null;
  const sorted = [...steps].sort((a, b) => {
    const aOrder = STEP_ORDER[a.etapa] ?? 99;
    const bOrder = STEP_ORDER[b.etapa] ?? 99;
    if (aOrder !== bOrder) return aOrder - bOrder;
    const aStatus = STEP_STATUS_ORDER[a.status] ?? 99;
    const bStatus = STEP_STATUS_ORDER[b.status] ?? 99;
    return aStatus - bStatus;
  });
  return sorted[0]?.status ?? null;
}

function StatusBadge({ status, step }: { status: string; step?: string | null }) {
  const classStatus = step ?? status;
  const className = `${styles.badge} ${styles[`badge_${classStatus.toLowerCase()}`] || styles.badge_pending}`;
  return (
    <span className={className}>
      <span className={styles.badgeDot} />
      {step ? `${status} (${step})` : status}
    </span>
  );
}

export function Extrair() {
  const navigate = useNavigate();
  const [url, setUrl] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [extracoes, setExtracoes] = useState<ExtracaoResult[]>([]);
  const [polling, setPolling] = useState(false);
  const [scannerOpen, setScannerOpen] = useState(false);

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

  const handleReprocess = async (id: number, ev: React.MouseEvent) => {
    ev.stopPropagation();
    setError(null);
    try {
      await reprocessarExtracao(id);
      await fetchExtracoes();
    } catch (err) {
      const message =
        err instanceof FetchError
          ? err.message
          : "Erro ao reprocessar extração";
      setError(message);
    }
  };

  const handleQrScan = useCallback((scannedUrl: string) => {
    setUrl(scannedUrl);
    setScannerOpen(false);
  }, []);

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
          <div className={styles.inputRow}>
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
              type="button"
              onClick={() => setScannerOpen(true)}
              className={styles.cameraButton}
              aria-label="Escanear QR Code"
              disabled={loading}
            >
              📷
            </button>
          </div>
          <button
            type="submit"
            className={styles.button}
            disabled={loading || !url}
          >
            {loading ? "Extraindo..." : "Extrair"}
          </button>
        </form>

        <QrCodeScanner
          open={scannerOpen}
          onScan={handleQrScan}
          onClose={() => setScannerOpen(false)}
        />
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
              <span className={styles.colAction} />
            </div>
              {extracoes.map((e) => (
              <div
                key={e.id_extracao}
                className={styles.tableRow}
                onClick={() => navigate(`/extracao/${e.id_extracao}`)}
                role="button"
                tabIndex={0}
                onKeyDown={(ev) => {
                  if (ev.key === "Enter" || ev.key === " ") {
                    ev.preventDefault();
                    navigate(`/extracao/${e.id_extracao}`);
                  }
                }}
              >
                <span className={styles.colId}>{e.id_extracao}</span>
                <span className={styles.colData}>
                  {new Date(e.created_at).toLocaleString("pt-BR")}
                </span>
                <span className={styles.colStatus}>
                  <StatusBadge status={e.status} step={latestStep(e.steps)} />
                </span>
                <span className={styles.colAction}>
                  {(e.status === "DONE" || e.status === "ERROR") && (
                    <button
                      type="button"
                      className={styles.reprocessButton}
                      onClick={(ev) => handleReprocess(e.id_extracao, ev)}
                    >
                      {e.status === "ERROR" ? "Reprocessar" : "Processar"}
                    </button>
                  )}
                </span>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}