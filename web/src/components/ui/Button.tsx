import type { ButtonHTMLAttributes } from "react";
import ui from "./ui.module.css";

type Variant = "primary" | "secondary" | "ghost" | "danger";
type Size = "sm" | "md";

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: Variant;
  size?: Size;
}

export function Button({
  variant = "primary",
  size = "md",
  className,
  type = "button",
  ...rest
}: ButtonProps) {
  const cls = [ui.button, ui[size], ui[variant], className]
    .filter(Boolean)
    .join(" ");

  return <button type={type} className={cls} {...rest} />;
}
