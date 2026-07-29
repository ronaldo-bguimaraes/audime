import { Loader2 } from "lucide-react";
import styles from "./LoadingSpinner.module.css";

interface Props {
  message?: string;
}

export function LoadingSpinner({ message = "Carregando..." }: Props) {
  return (
    <div className={styles.container}>
      <Loader2 size={32} className={styles.spinner} />
      <p className={styles.message}>{message}</p>
    </div>
  );
}
