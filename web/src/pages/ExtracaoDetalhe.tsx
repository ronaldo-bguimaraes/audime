import { useParams, useNavigate } from "react-router";
import { useFetch } from "../hooks/useFetch";
import { usePolling } from "../hooks/usePolling";
import { listarExtracoes, type ExtracaoResult, type PipelineStep } from "../api/extracoes";
import { LoadingSpinner } from "../components/LoadingSpinner";
import { ErrorMessage } from "../components/ErrorMessage";
import { QrCodeDisplay } from "../components/QrCodeDisplay";

import styles from "./ExtracaoDetalhe.module.css";

const STEP_LABELS: Record<string, string> = {
  RAW_IMPORT: "Importação",
  STAGING: "Normalização",
  ANALYTICS: "Analytics",
  COMPLETE: "Concluído",
};

const STEP_ICONS: Record<string, string> = {
  PENDING: "○",
  RUNNING: "◌",
  DONE: "✓",
  ERROR: "✗",
};

const STATUS_ATIVOS = new Set(["PENDING", "RUNNING"]);

function StepIcon({ status }: { status: string }) {
  const icon = STEP_ICONS[status] || "○";
  return <div className={`${styles.stepIcon} ${styles[`step${status}`] || ""}`}>{icon}</div>;
}

function StepBadge({ status }: { status: string }) {
  return (
    <span className={`${styles.stepBadge} ${styles[`badge${status}`] || ""}`}>
      {status}
    </span>
  );
}

function TimelineStep({ step }: { step: PipelineStep }) {
  const stepLabel = STEP_LABELS[step.etapa] || step.etapa;
  const hasTiming = step.iniciado_em || step.concluido_em;
  return (
    <li className={styles.step}>
      <StepIcon status={step.status} />
      <div className={styles.stepHeader}>
        <span className={styles.stepName}>{stepLabel}</span>
        <StepBadge status={step.status} />
      </div>
      {hasTiming && (
        <p className={styles.stepMeta}>
          {step.iniciado_em && `Início: ${new Date(step.iniciado_em).toLocaleString("pt-BR")}`}
          {step.concluido_em && step.iniciado_em !== step.concluido_em && (
            <> &middot; Fim: {new Date(step.concluido_em!).toLocaleString("pt-BR")}</>
          )}
        </p>
      )}
      {step.mensagem && <p className={styles.stepMessage}>{step.mensagem}</p>}
    </li>
  );
}

export function ExtracaoDetalhe() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const idExtracao = Number(id);

  const fetchExtracao = async (): Promise<ExtracaoResult | null> => {
    const list = await listarExtracoes(100);
    return list.find((e) => e.id_extracao === idExtracao) ?? null;
  };

  const { data, loading, error, refetch } = useFetch<ExtracaoResult | null>(
    fetchExtracao,
    [idExtracao],
  );

  const isAtivo = data ? STATUS_ATIVOS.has(data.status) : false;
  usePolling(refetch, isAtivo ? 5000 : null);

  if (loading) {
    return (
      <div className={styles.container}>
        <LoadingSpinner message="Carregando extração..." />
      </div>
    );
  }

  if (error) {
    return (
      <div className={styles.container}>
        <ErrorMessage
          message={error.includes("404") ? "Extração não encontrada" : error}
          onRetry={refetch}
        />
      </div>
    );
  }

  if (!data) {
    return (
      <div className={styles.container}>
        <ErrorMessage message="Extração não encontrada" />
      </div>
    );
  }

  const stepsOrdenados = [...(data.steps || [])].sort((a, b) => a.ordem - b.ordem);

  return (
    <div className={styles.container}>
      <button
        type="button"
        className={styles.backButton}
        onClick={() => navigate("/extrair")}
      >
        ← Voltar
      </button>

      <div className={styles.card}>
        <h1 className={styles.title}>Extração #{data.id_extracao}</h1>
        <p className={styles.subtitle}>
          Criada em {new Date(data.created_at).toLocaleString("pt-BR")}
        </p>
        <div className={styles.infoRow}>
          <span className={styles.infoLabel}>Status</span>
          <span className={styles.infoValue}>{data.status}</span>
        </div>
        <div className={styles.infoRow}>
          <span className={styles.infoLabel}>URL</span>
          <span className={styles.infoValue}>
            <QrCodeDisplay url={data.url} />
          </span>
        </div>
        {data.reprocess_count != null && data.reprocess_count > 0 && (
          <div className={styles.infoRow}>
            <span className={styles.infoLabel}>Reprocessos</span>
            <span className={styles.infoValue}>{data.reprocess_count}</span>
          </div>
        )}
      </div>

      <div className={styles.card}>
        <h2 style={{ margin: "0 0 16px", fontSize: "1.1rem" }}>Pipeline</h2>
        {stepsOrdenados.length === 0 ? (
          <p style={{ color: "var(--text-secondary)", fontSize: "0.875rem" }}>
            Nenhuma etapa encontrada.
          </p>
        ) : (
          <ol className={styles.timeline}>
            {stepsOrdenados.map((step) => (
              <TimelineStep key={step.etapa} step={step} />
            ))}
          </ol>
        )}
      </div>
    </div>
  );
}
