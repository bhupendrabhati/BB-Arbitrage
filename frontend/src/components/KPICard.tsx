"use client";

import { clsx } from "clsx";
import { ReactNode } from "react";

interface KPICardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  icon?: ReactNode;
  trend?: "up" | "down" | "neutral";
  trendValue?: string;
  limit?: string;
  used?: number;
  color?: "blue" | "green" | "red" | "yellow" | "cyan";
}

const colorMap = {
  blue: "from-accent/20 to-accent/5 border-accent/20",
  green: "from-success/20 to-success/5 border-success/20",
  red: "from-danger/20 to-danger/5 border-danger/20",
  yellow: "from-warning/20 to-warning/5 border-warning/20",
  cyan: "from-info/20 to-info/5 border-info/20",
};

const iconColorMap = {
  blue: "text-accent bg-accent/20",
  green: "text-success bg-success/20",
  red: "text-danger bg-danger/20",
  yellow: "text-warning bg-warning/20",
  cyan: "text-info bg-info/20",
};

const barColorMap = {
  blue: "bg-accent",
  green: "bg-success",
  red: "bg-danger",
  yellow: "bg-warning",
  cyan: "bg-info",
};

export default function KPICard({ title, value, subtitle, icon, trend, trendValue, limit, used, color = "blue" }: KPICardProps) {
  return (
    <div className={clsx(
      "relative overflow-hidden rounded-xl border bg-gradient-to-br p-5 transition-all duration-300 hover:scale-[1.02] hover:shadow-lg",
      colorMap[color]
    )}>
      <div className="flex items-start justify-between">
        <div className="space-y-2">
          <p className="text-xs font-medium uppercase tracking-wider text-slate-400">{title}</p>
          <p className="text-2xl font-bold text-white">{value}</p>
          {subtitle && <p className="text-xs text-slate-500">{subtitle}</p>}
          {limit && <p className="text-xs text-slate-500">{limit}</p>}
          {trend && trendValue && (
            <div className={clsx("flex items-center gap-1 text-xs font-medium",
              trend === "up" && "text-success",
              trend === "down" && "text-danger",
              trend === "neutral" && "text-slate-400"
            )}>
              <span>{trend === "up" ? "▲" : trend === "down" ? "▼" : "—"}</span>
              <span>{trendValue}</span>
            </div>
          )}
        </div>
        {icon && (
          <div className={clsx("w-10 h-10 rounded-lg flex items-center justify-center", iconColorMap[color])}>
            {icon}
          </div>
        )}
      </div>
      {typeof used === "number" && (
        <div className="mt-3 h-1.5 bg-dark-600 rounded-full overflow-hidden">
          <div className={clsx("h-full rounded-full transition-all duration-500", barColorMap[color])} style={{ width: `${Math.min(used, 100)}%` }} />
        </div>
      )}
    </div>
  );
}
