"use client";

import { useEffect, useState } from "react";
import DashboardLayout from "@/components/DashboardLayout";
import Badge from "@/components/Badge";
import { api } from "@/lib/api";
import { ArrowLeftRight, Download } from "lucide-react";

interface Trade {
  id: string;
  symbol: string;
  mode: string;
  buy_exchange: string;
  sell_exchange: string;
  buy_price: string;
  sell_price: string;
  quantity: string;
  buy_fee: string;
  sell_fee: string;
  slippage: string;
  net_profit: string;
  status: string;
  created_at: string;
}

export default function TradesPage() {
  const [trades, setTrades] = useState<Trade[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const load = async () => {
      try {
        const data = await api.trades();
        setTrades((data.trades as Trade[]) || []);
      } catch {}
      setLoading(false);
    };
    load();
  }, []);

  const exportCSV = () => {
    if (trades.length === 0) return;
    const headers = ["ID", "Symbol", "Mode", "Buy Exchange", "Sell Exchange", "Buy Price", "Sell Price", "Quantity", "Fees", "Net Profit", "Status", "Date"];
    const rows = trades.map(t => [t.id, t.symbol, t.mode, t.buy_exchange, t.sell_exchange, t.buy_price, t.sell_price, t.quantity, `${Number(t.buy_fee) + Number(t.sell_fee)}`, t.net_profit, t.status, t.created_at]);
    const csv = [headers.join(","), ...rows.map(r => r.join(","))].join("\n");
    const blob = new Blob([csv], { type: "text/csv" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "trades.csv";
    a.click();
  };

  return (
    <DashboardLayout>
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-white">Trades</h1>
            <p className="text-sm text-slate-400 mt-1">All executed and simulated trades</p>
          </div>
          <button
            onClick={exportCSV}
            className="flex items-center gap-2 px-4 py-2 rounded-lg bg-accent/15 text-accent border border-accent/30 text-sm font-medium hover:bg-accent/25 transition-colors"
          >
            <Download className="w-4 h-4" />
            Export CSV
          </button>
        </div>

        {loading ? (
          <div className="flex items-center justify-center h-64">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-accent" />
          </div>
        ) : trades.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-64 text-slate-500">
            <ArrowLeftRight className="w-12 h-12 mb-3 opacity-50" />
            <p className="text-lg font-medium">No trades yet</p>
            <p className="text-sm">Trades will appear here when executed</p>
          </div>
        ) : (
          <div className="overflow-x-auto rounded-xl border border-dark-600">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-dark-600 bg-dark-700/50">
                  <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wider text-slate-400">Symbol</th>
                  <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wider text-slate-400">Mode</th>
                  <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wider text-slate-400">Buy</th>
                  <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wider text-slate-400">Sell</th>
                  <th className="px-4 py-3 text-right text-xs font-semibold uppercase tracking-wider text-slate-400">Buy Price</th>
                  <th className="px-4 py-3 text-right text-xs font-semibold uppercase tracking-wider text-slate-400">Sell Price</th>
                  <th className="px-4 py-3 text-right text-xs font-semibold uppercase tracking-wider text-slate-400">Net Profit</th>
                  <th className="px-4 py-3 text-center text-xs font-semibold uppercase tracking-wider text-slate-400">Status</th>
                  <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wider text-slate-400">Date</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-dark-600">
                {trades.map((t) => (
                  <tr key={t.id} className="hover:bg-dark-700/30 transition-colors">
                    <td className="px-4 py-3 font-semibold text-white">{t.symbol}</td>
                    <td className="px-4 py-3"><Badge variant="purple">{t.mode}</Badge></td>
                    <td className="px-4 py-3 text-slate-300 text-xs">{t.buy_exchange}</td>
                    <td className="px-4 py-3 text-slate-300 text-xs">{t.sell_exchange}</td>
                    <td className="px-4 py-3 text-right font-mono text-slate-300">₹{t.buy_price}</td>
                    <td className="px-4 py-3 text-right font-mono text-slate-300">₹{t.sell_price}</td>
                    <td className="px-4 py-3 text-right font-mono">
                      <span className={Number(t.net_profit) >= 0 ? "text-success" : "text-danger"}>
                        ₹{t.net_profit}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-center">
                      <Badge variant={t.status === "completed" ? "success" : t.status === "failed" ? "danger" : "warning"}>
                        {t.status}
                      </Badge>
                    </td>
                    <td className="px-4 py-3 text-slate-400 text-xs">{new Date(t.created_at).toLocaleString()}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </DashboardLayout>
  );
}
