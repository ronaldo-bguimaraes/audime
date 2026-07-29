import { useState, useEffect, useCallback, type FormEvent } from "react";
import { useNavigate } from "react-router";
import { ScanLine, RotateCw } from "lucide-react";
import { criarExtracao, listarExtracoes, reprocessarExtracao, type ExtracaoResult, type PipelineStep } from "../api/extracoes";
import { FetchError } from "../api/client";
import { QrCodeScanner } from "../components/QrCodeScanner";
import styles from "./Extrair.module.css";

const STATUS_ATIVOS = new Set(["PENDING", "RUNNING"]);

const STEP_LABELS: Record<string, string> = {
  RAW_IMPORT: "Importação",
  STAGING: "Normalização",
  ANALYTICS: "Analytics",
  COMPLETE: "Concluído",
};

function activeStep(steps: PipelineStep[]): { etapa: string; status: string } | null {
  if (!steps.length) return null;
  const ordenados = [...steps].sort((a, b) => a.ordem - b.ordem);
  const ativo = ordenados.find((s) => s.status !== "DONE");
  return ativo
    ? { etapa: STEP_LABELS[ativo.etapa] || ativo.etapa, status: ativo.status }
    : { etapa: STEP_LABELS[ordenados[ordenados.length - 1].etapa] || ordenados[ordenados.length - 1].etapa, status: "DONE" };
}

function StatusBadge({ status }: { status: string }) {
  const cls = `${styles.badge} ${styles[`badge_${status.toLowerCase()}`] || styles.badge_pending}`;
  return (
    <span className={cls}>
      <span className={styles.badgeDot} />
      {status}
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
              <ScanLine size={20} />
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

      <div className={styles.listSection}>
        <h2 className={styles.listTitle}>Extrações Recentes</h2>
        {extracoes.length === 0 ? (
          <p className={styles.empty}>Nenhuma extração encontrada.</p>
        ) : (
          <div className={styles.list}>
            {extracoes.map((e) => (
              <div
                key={e.id_extracao}
                className={styles.historyCard}
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
                <div className={styles.historyCardTop}>
                  <div>
                    <h3 className={styles.historyCardTitle}>
                      Extração #{e.id_extracao}
                    </h3>
                    <p className={styles.historyCardDate}>
                      Criada em {new Date(e.created_at).toLocaleString("pt-BR")}
                    </p>
                  </div>
                    {(e.status === "DONE" || e.status === "ERROR") && (
                    <button
                      type="button"
                      className={styles.reprocessButton}
                      onClick={(ev) => handleReprocess(e.id_extracao, ev)}
                    >
                      <RotateCw size={12} />
                      Reprocessar
                    </button>
                  )}
                </div>
                <div className={styles.historyCardStatus}>
                  {(() => {
                    const s = activeStep(e.steps);
                    if (!s) return <StatusBadge status="—" />;
                    return (
                      <>
                        <span className={styles.historyCardStep}>{s.etapa}</span>
                        <StatusBadge status={s.status} />
                      </>
                    );
                  })()}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}