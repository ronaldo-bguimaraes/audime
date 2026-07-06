import { useRef, useEffect } from "react";
import { useQrCodeScanner } from "../hooks/useQrCodeScanner";
import styles from "../pages/Extrair.module.css";

interface QrCodeScannerProps {
  open: boolean;
  onScan: (url: string) => void;
  onClose: () => void;
}

/**
 * Modal component that displays a live camera feed and scans QR Codes.
 *
 * When a valid HTTP(S) URL is detected, it calls `onScan` and the parent
 * should close the modal. The user can also cancel via the Cancel button.
 */
export function QrCodeScanner({ open, onScan, onClose }: QrCodeScannerProps) {
  const videoRef = useRef<HTMLVideoElement | null>(null);

  const { status, errorMessage, startScanning, stopScanning } =
    useQrCodeScanner({ videoRef, onScan });

  useEffect(() => {
    if (open) {
      void startScanning();
    } else {
      stopScanning();
    }
    return () => {
      stopScanning();
    };
  }, [open, startScanning, stopScanning]);

  if (!open) return null;

  return (
    <div
      className={styles.modalOverlay}
      role="dialog"
      aria-modal="true"
      aria-label="Escanear QR Code"
    >
      <div className={styles.modal}>
        <button
          type="button"
          className={styles.modalClose}
          onClick={onClose}
          aria-label="Fechar"
        >
          &times;
        </button>

        <h2 className={styles.modalTitle}>Escanear QR Code</h2>

        {status === "error" ? (
          <div className={styles.cameraError} role="alert">
            {errorMessage}
          </div>
        ) : (
          <div className={styles.videoContainer}>
            <video
              ref={videoRef}
              autoPlay
              playsInline
              muted
              className={styles.video}
            />
          </div>
        )}

        <div className={styles.modalActions}>
          <button
            type="button"
            className={styles.cancelButton}
            onClick={onClose}
          >
            Cancelar
          </button>
        </div>
      </div>
    </div>
  );
}
