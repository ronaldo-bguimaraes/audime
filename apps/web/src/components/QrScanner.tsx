import { useEffect, useRef, useState } from "react";
import { Html5Qrcode } from "html5-qrcode";
import { Button } from "@/components/ui/button";

import "./QrScanner.css";

type ScanStatus = "idle" | "scanning" | "loading" | "success" | "error";

const API_ENDPOINT = "https://sua-api.com/qr";

// function validateQrCode(content: string): boolean {
//     try {
//         const url = new URL(content);
//         url.hostname

//     } catch {
//         return false;
//     }
// }

export default function QrScanner() {
    const [status, setStatus] = useState<ScanStatus>("idle");
    const [result, setResult] = useState<string | null>(null);
    const [apiResponse, setApiResponse] = useState<unknown>(null);
    const [errorMsg, setErrorMsg] = useState("");

    const scannerRef = useRef<Html5Qrcode | null>(null);
    const isScanningRef = useRef(false);

    useEffect(() => {
        return () => {
            if (scannerRef.current) {
                scannerRef.current.stop().catch(() => { });
            }
        };
    }, []);

    const startScanner = async () => {
        setStatus("scanning");
        setResult(null);
        setApiResponse(null);
        setErrorMsg("");

        const html5QrCode = new Html5Qrcode("qr-reader");
        scannerRef.current = html5QrCode;
        isScanningRef.current = true;

        try {
            await html5QrCode.start(
                { facingMode: "environment" },
                { fps: 10, qrbox: { width: 240, height: 240 } },
                async (decodedText) => {
                    if (!isScanningRef.current) return;

                    isScanningRef.current = false;
                    await html5QrCode.stop();

                    setResult(decodedText);
                    await sendToApi(decodedText);
                },
                () => {/* scan failure, ignore and continue scanning */ }
            );
        } catch (error) {
            setErrorMsg("Não foi possível acessar a câmera. Verifique as permissões.");
            setStatus("error");
        }
    };

    const stopScanner = async () => {
        isScanningRef.current = false;

        if (scannerRef.current) {
            try {
                await scannerRef.current.stop();
            } catch {
                // ignore errors when stopping
            }
        }

        setStatus("idle");
    };

    const sendToApi = async (content: string) => {
        setStatus("loading");

        try {
            const res = await fetch(API_ENDPOINT, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ qr_content: content }),
            });

            if (!res.ok) {
                throw new Error(`HTTP ${res.status}`);
            }

            const data = await res.json();
            setApiResponse(data);
            setStatus("success");
        } catch (error) {
            setErrorMsg(
                `Erro ao enviar para a API: ${error instanceof Error ? error.message : "erro inesperado"}`
            );
            setStatus("error");
        }
    };

    const reset = () => {
        setStatus("idle");
        setResult(null);
        setApiResponse(null);
        setErrorMsg("");
    };

    return (
        <div className="mx-auto flex min-h-screen w-full max-w-4xl flex-col gap-6 px-4 py-8 sm:px-6 lg:px-8">
            <div className="rounded-3xl border border-border bg-card p-6 shadow-sm">
                <div className="space-y-2">
                    <h1 className="text-3xl font-semibold tracking-tight text-foreground">Scanner QR</h1>
                    <p className="text-sm text-muted-foreground">
                        Aponte para o código e permita o uso da câmera do dispositivo.
                    </p>
                </div>
            </div>

            <div className="rounded-3xl border border-border bg-background/80 p-6 shadow-sm">
                <div className="relative overflow-hidden rounded-3xl border border-border bg-slate-950/70 px-4 py-4 sm:px-6">
                    <div className="relative min-h-[320px] overflow-hidden rounded-3xl bg-black">
                        <div id="qr-reader" className="absolute inset-0" />

                        <div className="pointer-events-none absolute left-4 top-4 h-6 w-6 border-l-2 border-t-2 border-accent" />
                        <div className="pointer-events-none absolute right-4 top-4 h-6 w-6 border-r-2 border-t-2 border-accent" />
                        <div className="pointer-events-none absolute left-4 bottom-4 h-6 w-6 border-l-2 border-b-2 border-accent" />
                        <div className="pointer-events-none absolute right-4 bottom-4 h-6 w-6 border-r-2 border-b-2 border-accent" />

                        {status === "idle" && (
                            <div className="absolute inset-0 flex flex-col items-center justify-center gap-3 bg-slate-950/70 text-center text-sm uppercase tracking-[0.2em] text-muted-foreground">
                                <div className="inline-flex h-14 w-14 items-center justify-center rounded-2xl border border-border">
                                    <span className="text-2xl">📷</span>
                                </div>
                                <span>Câmera desligada</span>
                            </div>
                        )}

                        {status === "loading" && (
                            <div className="absolute inset-0 flex flex-col items-center justify-center gap-3 bg-slate-950/85 text-sm uppercase tracking-[0.2em] text-accent">
                                <div className="h-10 w-10 animate-spin rounded-full border-4 border-border border-t-accent" />
                                <span>Enviando...</span>
                            </div>
                        )}
                    </div>

                    <div className="mt-5 flex flex-col gap-3 sm:flex-row">
                        {status === "idle" && (
                            <Button className="min-w-[180px]" onClick={startScanner}>
                                Iniciar scanner
                            </Button>
                        )}
                        {status === "scanning" && (
                            <Button variant="secondary" className="min-w-[180px]" onClick={stopScanner}>
                                Cancelar
                            </Button>
                        )}
                        {(status === "success" || status === "error") && (
                            <Button className="min-w-[180px]" onClick={reset}>
                                Escanear novamente
                            </Button>
                        )}
                    </div>
                </div>

                {(result || status === "error" || status === "success") && (
                    <div className="mt-6 space-y-4">
                        {result && (
                            <div className="rounded-3xl border border-border bg-card p-4">
                                <div className="mb-2 text-xs uppercase tracking-[0.24em] text-muted-foreground">
                                    Conteúdo lido
                                </div>
                                <div className="text-sm text-foreground break-words">{result}</div>
                            </div>
                        )}

                        {status === "error" && (
                            <div className="rounded-3xl border border-border bg-card p-4">
                                <div className="mb-2 text-xs uppercase tracking-[0.24em] text-rose-400">✗ Erro</div>
                                <div className="text-sm text-foreground break-words">{errorMsg}</div>
                            </div>
                        )}
                    </div>
                )}
            </div>
        </div>
    );
}
