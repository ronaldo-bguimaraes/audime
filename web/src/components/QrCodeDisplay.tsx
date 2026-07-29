import { useEffect, useState, useCallback, useRef } from "react";
import { ExternalLink, Copy, CheckCircle2 } from "lucide-react";
import QRCode from "qrcode";
import styles from "./QrCodeDisplay.module.css";

interface Props {
  url: string | null | undefined;
}

/** Fallback copy using a temporary textarea when navigator.clipboard is unavailable. */
function copyWithFallback(text: string): Promise<void> {
  if (navigator.clipboard?.writeText) {
    return navigator.clipboard.writeText(text);
  }
  return new Promise((resolve, reject) => {
    const textarea = document.createElement("textarea");
    textarea.value = text;
    textarea.style.position = "fixed";
    textarea.style.left = "-9999px";
    document.body.appendChild(textarea);
    textarea.select();
    const ok = document.execCommand("copy");
    document.body.removeChild(textarea);
    if (ok) {
      resolve();
    } else {
      reject(new Error("clipboard copy failed"));
    }
  });
}

export function QrCodeDisplay({ url }: Props) {
  const [qrDataUrl, setQrDataUrl] = useState<string | null>(null);
  const [copied, setCopied] = useState(false);
  const cancelledRef = useRef(false);

  useEffect(() => {
    cancelledRef.current = false;

    if (!url) {
      // eslint-disable-next-line react-hooks/set-state-in-effect
      setQrDataUrl(null);
      return;
    }

    QRCode.toDataURL(url, { width: 180, margin: 2 })
      .then((dataUrl) => {
        if (!cancelledRef.current) {
          setQrDataUrl(dataUrl);
        }
      })
      .catch(() => {
        if (!cancelledRef.current) {
          setQrDataUrl(null);
        }
      });

    return () => {
      cancelledRef.current = true;
    };
    // NOTE: setQrDataUrl(null) is called synchronously when url is falsy.
    // This is acceptable because it's paired with an early return:
    // no async work is started, so there is no risk of cascading or stale updates.
    // See https://react.dev/learn/you-might-not-need-an-effect
  }, [url]);

  const handleCopy = useCallback(async () => {
    if (!url) return;
    try {
      await copyWithFallback(url);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {
      setCopied(false);
    }
  }, [url]);

  // No URL → show fallback text only
  if (!url) {
    return <span className={styles.fallback}>—</span>;
  }

  // Loading state: URL is present but QR data not yet generated
  const isLoading = url && !qrDataUrl;

  return (
    <div className={styles.qrContainer}>
      {isLoading ? (
        <div className={styles.qrPlaceholder} aria-label="Gerando QR Code…" />
      ) : qrDataUrl ? (
        <img
          src={qrDataUrl}
          alt="QR Code para acessar a URL desta extração"
          className={styles.qrImage}
        />
      ) : (
        <span className={styles.fallback}>{url}</span>
      )}

      <div className={styles.actionRow}>
        <a
          href={url}
          target="_blank"
          rel="noopener noreferrer"
          className={styles.actionButton}
          aria-label="Abrir URL"
        >
          <ExternalLink size={16} />
          <span>Abrir</span>
        </a>
        <button
          type="button"
          onClick={handleCopy}
          className={styles.actionButton}
          aria-label="Copiar URL para a área de transferência"
        >
          {copied ? <CheckCircle2 size={16} /> : <Copy size={16} />}
          <span>{copied ? "Copiado!" : "Copiar"}</span>
        </button>
      </div>

      {copied && (
        <span className={styles.srOnly} role="status" aria-live="polite">
          URL copiada para a área de transferência
        </span>
      )}
    </div>
  );
}
