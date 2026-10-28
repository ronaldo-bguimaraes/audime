import type { CSSProperties } from "react";
import ui from "./ui.module.css";

interface SkeletonProps {
  width?: string | number;
  height?: string | number;
  radius?: string;
  className?: string;
  style?: CSSProperties;
}

export function Skeleton({
  width = "100%",
  height = 12,
  radius,
  className,
  style,
}: SkeletonProps) {
  return (
    <span
      aria-hidden="true"
      className={[ui.skeleton, className].filter(Boolean).join(" ")}
      style={{ width, height, borderRadius: radius, ...style }}
    />
  );
}
