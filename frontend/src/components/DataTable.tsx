"use client";

import { ReactNode } from "react";

interface Column<T> {
  key: string;
  label: string;
  render?: (item: T) => ReactNode;
  sortable?: boolean;
}

interface DataTableProps<T> {
  columns: Column<T>[];
  data: T[];
  emptyMessage?: string;
}

export default function DataTable<T extends Record<string, unknown>>({ columns, data, emptyMessage = "No data" }: DataTableProps<T>) {
  return (
    <div className="overflow-x-auto rounded-xl border border-dark-600">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-dark-600 bg-dark-700/50">
            {columns.map((col) => (
              <th key={col.key} className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wider text-slate-400">
                {col.label}
              </th>
            ))}
          </tr>
        </thead>
        <tbody className="divide-y divide-dark-600">
          {data.length === 0 ? (
            <tr>
              <td colSpan={columns.length} className="px-4 py-8 text-center text-slate-500">
                {emptyMessage}
              </td>
            </tr>
          ) : (
            data.map((item, i) => (
              <tr key={i} className="hover:bg-dark-700/30 transition-colors">
                {columns.map((col) => (
                  <td key={col.key} className="px-4 py-3 text-slate-300">
                    {col.render ? col.render(item) : String(item[col.key] ?? "")}
                  </td>
                ))}
              </tr>
            ))
          )}
        </tbody>
      </table>
    </div>
  );
}
