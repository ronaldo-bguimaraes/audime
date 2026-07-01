import { useState, useEffect, useRef, type FormEvent } from "react";
import { useNavigate } from "react-router";
import { useAuth } from "../hooks/useAuth";
import { FetchError } from "../api/client";
import styles from "./Login.module.css";

type LoginPhase = "idle" | "sending" | "codeSent" | "verifying" | "error";

export function Login() {
  const { isAuthenticated, sendCode, verify, loading } = useAuth();
  const navigate = useNavigate();

  const [phase, setPhase] = useState<LoginPhase>("idle");
  const [email, setEmail] = useState("");
  const [code, setCode] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [timeLeft, setTimeLeft] = useState(0);
  const timerRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const clearTimer = () => {
    if (timerRef.current) {
      clearInterval(timerRef.current);
      timerRef.current = null;
    }
  };

  // Redireciona se já autenticado
  useEffect(() => {
    if (isAuthenticated) {
      navigate("/dashboard", { replace: true });
    }
  }, [isAuthenticated, navigate]);

  // Contagem regressiva para reenvio
  useEffect(() => {
    if (phase === "codeSent" && timeLeft > 0) {
      timerRef.current = setInterval(() => {
        setTimeLeft((prev) => {
          if (prev <= 1) {
            clearTimer();
            return 0;
          }
          return prev - 1;
        });
      }, 1000);
    }
    return clearTimer;
  }, [phase, timeLeft]);

  const handleSendCode = async (e: FormEvent) => {
    e.preventDefault();
    setError(null);
    setPhase("sending");
    try {
      await sendCode(email);
      localStorage.setItem("pending_email", email);
      setPhase("codeSent");
      setTimeLeft(60);
    } catch (err) {
      const message =
        err instanceof FetchError ? err.message : "Erro ao enviar código";
      setError(message);
      setPhase("error");
    }
  };

  const handleVerify = async (e: FormEvent) => {
    e.preventDefault();
    if (code.length !== 6) return;
    setError(null);
    setPhase("verifying");
    try {
      await verify(code);
      // useAuth will update isAuthenticated, which triggers redirect
    } catch (err) {
      const message =
        err instanceof FetchError ? err.message : "Código inválido";
      setError(message);
      setPhase("codeSent");
    }
  };

  const handleResend = () => {
    setPhase("idle");
    setCode("");
    setError(null);
    setTimeLeft(0);
  };

  const handleCodeChange = (value: string) => {
    const digits = value.replace(/\D/g, "").slice(0, 6);
    setCode(digits);
  };

  return (
    <div className={styles.container}>
      <div className={styles.card}>
        <h1 className={styles.title}>audime</h1>
        <p className={styles.subtitle}>
          Gestão de gastos pessoais com NFC-e
        </p>

        {error && (
          <div className={styles.error} role="alert">
            {error}
          </div>
        )}

        {phase !== "codeSent" && phase !== "verifying" ? (
          /* Etapa 1: solicitar email */
          <form onSubmit={handleSendCode} className={styles.form}>
            <label htmlFor="login-email" className={styles.label}>
              Seu e-mail
            </label>
            <input
              id="login-email"
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="seu@email.com"
              className={styles.input}
              autoComplete="email"
              disabled={loading}
            />
            <button
              type="submit"
              className={styles.button}
              disabled={loading || !email}
            >
              {loading ? "Enviando..." : "Enviar código"}
            </button>
          </form>
        ) : (
          /* Etapa 2: verificar código */
          <form onSubmit={handleVerify} className={styles.form}>
            <p className={styles.codeSentMsg}>
              Código enviado para <strong>{email}</strong>
            </p>
            <label htmlFor="login-code" className={styles.label}>
              Código de verificação
            </label>
            <input
              id="login-code"
              type="text"
              inputMode="numeric"
              autoComplete="one-time-code"
              maxLength={6}
              value={code}
              onChange={(e) => handleCodeChange(e.target.value)}
              placeholder="000000"
              className={styles.codeInput}
              disabled={loading}
            />
            <button
              type="submit"
              className={styles.button}
              disabled={loading || code.length !== 6}
            >
              {loading ? "Verificando..." : "Verificar"}
            </button>
            <div className={styles.resendArea}>
              {timeLeft > 0 ? (
                <span className={styles.cooldown}>
                  Reenviar em {timeLeft}s
                </span>
              ) : (
                <button
                  type="button"
                  className={styles.resendBtn}
                  onClick={handleResend}
                  disabled={loading}
                >
                  Reenviar código
                </button>
              )}
            </div>
          </form>
        )}
      </div>
    </div>
  );
}
