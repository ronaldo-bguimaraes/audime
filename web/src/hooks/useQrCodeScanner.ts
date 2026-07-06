import { useRef, useCallback, useState, type RefObject } from "react";
import QrScanner from "qr-scanner";

export type ScannerStatus = "idle" | "scanning" | "error";

export interface UseQrCodeScannerOptions {
  videoRef: RefObject<HTMLVideoElement | null>;
  onScan: (url: string) => void;
}

export interface UseQrCodeScannerReturn {
  status: ScannerStatus;
  errorMessage: string | null;
  startScanning: () => Promise<void>;
  stopScanning: () => void;
}

/**
 * Hook that manages a QR Code scanner lifecycle using `qr-scanner`.
 *
 * Provides start/stop control, reports status changes, and exposes a
 * window.__injectQrResult test seam for Playwright integration.
 */
export function useQrCodeScanner({
  videoRef,
  onScan,
}: UseQrCodeScannerOptions): UseQrCodeScannerReturn {
  const scannerRef = useRef<QrScanner | null>(null);
  const [status, setStatus] = useState<ScannerStatus>("idle");
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const handleDecode = useCallback(
    (result: QrScanner.ScanResult) => {
      const url = result.data;
      if (/^https?:\/\//.test(url)) {
        onScan(url);
      }
      // Non-http results are ignored — scanner continues
    },
    [onScan],
  );

  const handleDecodeError = useCallback(() => {
    // Decode errors are expected between frames; ignore silently
  }, []);

  const startScanning = useCallback(async () => {
    if (!videoRef.current) return;

    setStatus("scanning");
    setErrorMessage(null);

    try {
      // Expose test seam so Playwright can inject QR results
      const injectFn = (url: string) => {
        if (/^https?:\/\//.test(url)) {
          onScan(url);
        }
      };
      (window as unknown as Record<string, unknown>).__injectQrResult = injectFn;

      const scanner = new QrScanner(
        videoRef.current,
        handleDecode,
        {
          onDecodeError: handleDecodeError,
          preferredCamera: "environment",
          maxScansPerSecond: 5,
          returnDetailedScanResult: true,
        },
      );
      scannerRef.current = scanner;
      await scanner.start();
    } catch (err: unknown) {
      setStatus("error");
      if (err instanceof DOMException) {
        switch (err.name) {
          case "NotAllowedError":
            setErrorMessage(
              "Acesso à câmera negado. Permita o acesso nas configurações do navegador.",
            );
            break;
          case "NotFoundError":
            setErrorMessage(
              "Nenhuma câmera encontrada no dispositivo.",
            );
            break;
          case "NotReadableError":
            setErrorMessage(
              "Câmera indisponível. Feche outros aplicativos que estejam usando a câmera.",
            );
            break;
          case "AbortError":
            setErrorMessage(
              "Não foi possível acessar a câmera.",
            );
            break;
          default:
            setErrorMessage(
              `Erro ao acessar a câmera: ${err.message}`,
            );
        }
      } else {
        setErrorMessage(
          "Câmera não disponível. Verifique as permissões do navegador.",
        );
      }
    }
  }, [videoRef, handleDecode, handleDecodeError, onScan]);

  const stopScanning = useCallback(() => {
    setStatus("idle");
    setErrorMessage(null);

    // Remove test seam
    delete (window as unknown as Record<string, unknown>).__injectQrResult;

    if (scannerRef.current) {
      scannerRef.current.stop();
      scannerRef.current.destroy();
      scannerRef.current = null;
    }
  }, []);

  return { status, errorMessage, startScanning, stopScanning };
}
