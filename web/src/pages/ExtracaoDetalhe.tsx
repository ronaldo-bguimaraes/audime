import { useParams, useNavigate } from "react-router";
import { useState } from "react";
import { ArrowLeft, Loader2, Check, X, Circle, ChevronDown, Copy } from "lucide-react";
import { useFetch } from "../hooks/useFetch";
import { usePolling } from "../hooks/usePolling";
import { listarExtracoes, type ExtracaoResult, type PipelineStep } from "../api/extracoes";
import { LoadingSpinner } from "../components/LoadingSpinner";
import { ErrorMessage } from "../components/ErrorMessage";

import styles from "./ExtracaoDetalhe.module.css";

const STEP_LABELS: Record<string, string> = {
  RAW_IMPORT: "Importação",
  STAGING: "Normalização",
  ANALYTICS: "Analytics",
  COMPLETE: "Concluído",
};

const STATUS_ATIVOS = new Set(["PENDING", "RUNNING"]);

function formatDuration(ms: number): string {
  if (ms < 1000) return `${ms}ms`;
  if (ms < 60000) return `${(ms / 1000).toFixed(1)}s`;
  const mins = Math.floor(ms / 60000);
  const secs = Math.floor((ms % 60000) / 1000);
  return `${mins}m ${secs}s`;
}

function StepIcon({ status }: { status: string }) {
  if (status === "DONE") return <Check size={14} className={styles.iconDone} />;
  if (status === "ERROR") return <X size={14} className={styles.iconError} />;
  if (status === "RUNNING") return <Loader2 size={14} className={styles.spinIcon} />;
  return <Circle size={14} className={styles.iconWaiting} />;
}

function TimelineStep({ step }: { step: PipelineStep }) {
  const label = STEP_LABELS[step.etapa] || step.etapa;
  const isWaiting = step.status === "PENDING";

  const duration = step.iniciado_em && step.concluido_em
    ? formatDuration(new Date(step.concluido_em).getTime() - new Date(step.iniciado_em).getTime())
    : null;

  const cls = [
    styles.step,
    isWaiting ? styles.waiting : "",
    step.status === "RUNNING" ? styles.running : "",
    step.status === "ERROR" ? styles.errored : "",
  ].filter(Boolean).join(" ");

  return (
    <div className={cls}>
      <div className={styles.stepIcon}>
        <StepIcon status={step.status} />
      </div>
      <div className={styles.stepBody}>
        <div className={styles.stepRow}>
          <span className={styles.stepName}>{label}</span>
          {duration && <span className={styles.stepTime}>{duration}</span>}
        </div>
        {step.mensagem && <p className={styles.stepMessage}>{step.mensagem}</p>}
      </div>
    </div>
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

  const [copied, setCopied] = useState(false);

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

  const handleCopy = async () => {
    if (data?.url) {
      await navigator.clipboard.writeText(data.url);
      setCopied(true);
      setTimeout(() => setCopied(false), 1500);
    }
  };

  const steps = [...(data.steps || [])].sort((a, b) => a.ordem - b.ordem);
  const total = steps.length;
  const done = steps.filter((s) => s.status === "DONE").length;
  const progress = total > 0 ? Math.round((done / total) * 100) : 0;
  const isAllDone = steps.every((s) => s.status === "DONE");
  const hasError = steps.some((s) => s.status === "ERROR");
  const isRunning = steps.some((s) => s.status === "RUNNING" || s.status === "PENDING");

  const logEntries = steps.flatMap((s) => {
    const label = STEP_LABELS[s.etapa] || s.etapa;
    const entries: { time: string; text: string }[] = [];
    if (s.iniciado_em) {
      entries.push({ time: new Date(s.iniciado_em).toLocaleTimeString("pt-BR"), text: `${label} iniciado` });
    }
    if (s.status === "DONE" && s.concluido_em) {
      entries.push({ time: new Date(s.concluido_em).toLocaleTimeString("pt-BR"), text: `${label} concluído` });
    }
    if (s.status === "ERROR" && s.mensagem) {
      entries.push({ time: new Date(s.iniciado_em ?? Date.now()).toLocaleTimeString("pt-BR"), text: `${label}: ${s.mensagem}` });
    }
    return entries;
  });

  return (
    <div className={styles.container}>
      <button
        type="button"
        className={styles.backButton}
        onClick={() => navigate("/extrair")}
      >
        <ArrowLeft size={16} /> Voltar
      </button>

      <div className={styles.card}>
        <h1 className={styles.title}>Extração #{data.id_extracao}</h1>
        <p className={styles.subtitle}>
          Criada em {new Date(data.created_at).toLocaleString("pt-BR")}
        </p>
        {data.url && (
          <div className={styles.infoRow}>
            <span className={styles.infoLabel}>URL</span>
            <span className={styles.urlValue}>
              <a
                href={data.url}
                target="_blank"
                rel="noopener noreferrer"
                className={styles.urlLink}
              >
                {data.url}
              </a>
              <button
                type="button"
                className={styles.copyButton}
                onClick={handleCopy}
                title="Copiar URL"
              >
                <Copy size={12} />
                {copied && <span className={styles.copyFeedback}>Copiado</span>}
              </button>
            </span>
          </div>
        )}
        {data.reprocess_count != null && data.reprocess_count > 0 && (
          <div className={styles.infoRow}>
            <span className={styles.infoLabel}>Reprocessos</span>
            <span className={styles.infoValue}>{data.reprocess_count}</span>
          </div>
        )}
      </div>

      <div className={styles.progressCard}>
        <div className={styles.progressHeader}>
          <span className={styles.progressTitle}>
            {hasError ? "Erro na importação" : isAllDone ? "Nota importada com sucesso" : "Importando nota"}
          </span>
          <span className={styles.progressStatus}>
            {hasError && <X size={14} className={styles.iconError} />}
            {!hasError && isAllDone && <Check size={14} className={styles.iconDone} />}
            {!hasError && isRunning && <Loader2 size={12} className={styles.spinIcon} />}
          </span>
        </div>

        {!hasError && isRunning && (
          <p className={styles.progressDesc}>Processando sua nota fiscal...</p>
        )}

        <div className={styles.progressTrack}>
          <div className={styles.progressFill} style={{ width: `${progress}%` }} />
        </div>
        <span className={styles.progressLabel}>{progress}%</span>

        {steps.length === 0 ? (
          <p className={styles.empty}>Nenhuma etapa encontrada.</p>
        ) : (
          <div className={styles.steps}>
            {steps.map((step) => (
              <TimelineStep key={step.etapa} step={step} />
            ))}
          </div>
        )}

        {logEntries.length > 0 && (
          <details className={styles.log}>
            <summary className={styles.logSummary}>
              <ChevronDown size={12} />
              Show details
            </summary>
            <div className={styles.logEntries}>
              {logEntries.map((entry, i) => (
                <div key={i} className={styles.logEntry}>
                  <span className={styles.logTime}>{entry.time}</span>
                  <span className={styles.logText}>{entry.text}</span>
                </div>
              ))}
            </div>
          </details>
        )}
      </div>
    </div>
  );
}
