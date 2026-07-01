import styles from "./LoadingSpinner.module.css";

interface Props {
  message?: string;
}

export function LoadingSpinner({ message = "Carregando..." }: Props) {
  return (
    <div className={styles.container}>
      <div className={styles.spinner} />
      <p className={styles.message}>{message}</p>
    </div>
  );
}
