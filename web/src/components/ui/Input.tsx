import type { InputHTMLAttributes } from "react";
import ui from "./ui.module.css";

interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  label: string;
  hint?: string;
  error?: string | null;
}

export function Input({ label, hint, error, id, className, ...rest }: InputProps) {
  const inputId = id ?? `input-${label.toLowerCase().replace(/\s+/g, "-")}`;

  return (
    <div className={ui.field}>
      <label htmlFor={inputId} className={ui.label}>
        {label}
      </label>
      <input
        id={inputId}
        className={[ui.input, error ? ui.inputError : "", className]
          .filter(Boolean)
          .join(" ")}
        aria-invalid={error ? true : undefined}
        aria-describedby={hint || error ? `${inputId}-hint` : undefined}
        {...rest}
      />
      {(error || hint) && (
        <span
          id={`${inputId}-hint`}
          className={error ? ui.errorText : ui.hint}
          role={error ? "alert" : undefined}
        >
          {error ?? hint}
        </span>
      )}
    </div>
  );
}
