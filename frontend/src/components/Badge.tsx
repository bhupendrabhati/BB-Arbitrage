"use client";

import { clsx } from "clsx";

type BadgeVariant = "success" | "danger" | "warning" | "info" | "neutral" | "purple";

const variantMap: Record<BadgeVariant, string> = {
  success: "bg-success/15 text-success border-success/30",
  danger: "bg-danger/15 text-danger border-danger/30",
  warning: "bg-warning/15 text-warning border-warning/30",
  info: "bg-info/15 text-info border-info/30",
  neutral: "bg-dark-600 text-slate-400 border-dark-500",
  purple: "bg-purple-500/15 text-purple-400 border-purple-500/30",
};

export default function Badge({ children, variant = "neutral" }: { children: React.ReactNode; variant?: BadgeVariant }) {
  return (
    <span className={clsx("inline-flex items-center px-2 py-0.5 rounded-full text-[11px] font-semibold border", variantMap[variant])}>
      {children}
    </span>
  );
}
