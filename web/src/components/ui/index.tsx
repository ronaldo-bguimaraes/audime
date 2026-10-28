import type { ReactNode } from "react";
import ui from "./ui.module.css";

export function EmptyState({
  icon,
  title,
  description,
  action,
}: {
  icon?: ReactNode;
  title: string;
  description?: ReactNode;
  action?: ReactNode;
}) {
  return (
    <div className={ui.empty}>
      {icon && <div className={ui.emptyIcon}>{icon}</div>}
      <span className={ui.emptyTitle}>{title}</span>
      {description && <p className={ui.emptyDescription}>{description}</p>}
      {action && <div className={ui.emptyAction}>{action}</div>}
    </div>
  );
}

export function Stat({
  label,
  value,
  hint,
  tone = "neutral",
  hero = false,
}: {
  label: string;
  value: ReactNode;
  hint?: ReactNode;
  tone?: "positive" | "negative" | "neutral";
  hero?: boolean;
}) {
  const toneClass =
    tone === "positive" ? ui.tonePositive : tone === "negative" ? ui.toneNegative : "";

  return (
    <div className={ui.stat}>
      <span className={ui.statLabel}>{label}</span>
      <span
        className={[ui.statValue, hero ? ui.statHero : "", toneClass]
          .filter(Boolean)
          .join(" ")}
      >
        {value}
      </span>
      {hint && <span className={ui.statHint}>{hint}</span>}
    </div>
  );
}
