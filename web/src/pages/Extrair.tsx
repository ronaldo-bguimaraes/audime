import { useState, type FormEvent } from "react";
import { useNavigate } from "react-router";
import { criarExtracao } from "../api/extracoes";
import { FetchError } from "../api/client";
import styles from "./Extrair.module.css";

export function Extrair() {
  const navigate = useNavigate();
  const [url, setUrl] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError(null);
    setSuccess(null);
    setLoading(true);

    try {
      await criarExtracao(url);
      setSuccess("Extração iniciada com sucesso!");
      setTimeout(() => {
        navigate("/dashboard");
      }, 2000);
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
            {success} Redirecionando...
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
    </div>
  );
}
