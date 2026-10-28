import type { HTMLAttributes, ReactNode } from "react";
import ui from "./ui.module.css";

interface CardProps extends HTMLAttributes<HTMLDivElement> {
  padding?: boolean;
}

export function Card({ padding = false, className, ...rest }: CardProps) {
  return (
    <div
      className={[ui.card, padding ? ui.cardPadding : "", className]
        .filter(Boolean)
        .join(" ")}
      {...rest}
    />
  );
}

export function CardHeader({
  title,
  subtitle,
  actions,
}: {
  title: ReactNode;
  subtitle?: ReactNode;
  actions?: ReactNode;
}) {
  return (
    <div className={ui.cardHeader}>
      <div>
        <div className={ui.cardTitle}>{title}</div>
        {subtitle && <div className={ui.cardSubtitle}>{subtitle}</div>}
      </div>
      {actions}
    </div>
  );
}
