import { AlertCircle } from "lucide-react";
import styles from "./ErrorMessage.module.css";

interface Props {
  message: string;
  onRetry?: () => void;
}

export function ErrorMessage({ message, onRetry }: Props) {
  return (
    <div className={styles.container} role="alert">
      <div className={styles.icon}>
        <AlertCircle size={20} />
      </div>
      <p className={styles.message}>{message}</p>
      {onRetry && (
        <button type="button" className={styles.retry} onClick={onRetry}>
          Tentar novamente
        </button>
      )}
    </div>
  );
}
