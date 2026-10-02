"use client";

import { ReactNode } from "react";

export default function ChartCard({ title, children, action }: { title: string; children: ReactNode; action?: ReactNode }) {
  return (
    <div className="rounded-xl border border-dark-600 bg-dark-800 p-5">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-sm font-semibold text-white">{title}</h3>
        {action}
      </div>
      {children}
    </div>
  );
}
