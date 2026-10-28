import type { ReactNode } from "react";
import ui from "./ui.module.css";

export type BadgeTone = "neutral" | "positive" | "negative" | "warning" | "progress";

const TONE_CLASS: Record<BadgeTone, string> = {
  neutral: "",
  positive: ui.badgePositive,
  negative: ui.badgeNegative,
  warning: ui.badgeWarning,
  progress: ui.badgeProgress,
};

export function Badge({
  tone = "neutral",
  dot = false,
  children,
}: {
  tone?: BadgeTone;
  dot?: boolean;
  children: ReactNode;
}) {
  return (
    <span className={[ui.badge, TONE_CLASS[tone]].filter(Boolean).join(" ")}>
      {dot && <span className={ui.dot} aria-hidden="true" />}
      {children}
    </span>
  );
}

/** Mapeia o status de extração da API para tom + rótulo do badge. */
export function statusTone(status: string): BadgeTone {
  switch (status.toUpperCase()) {
    case "DONE":
      return "positive";
    case "ERROR":
      return "negative";
    case "RUNNING":
    case "PENDING":
      return "progress";
    default:
      return "neutral";
  }
}

export function StatusBadge({ status }: { status: string }) {
  return (
    <Badge tone={statusTone(status)} dot>
      {status}
    </Badge>
  );
}
