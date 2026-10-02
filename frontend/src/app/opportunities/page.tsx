"use client";

import { useEffect, useState, Fragment } from "react";
import DashboardLayout from "@/components/DashboardLayout";
import Badge from "@/components/Badge";
import { api } from "@/lib/api";
import SmartSuggestions, { generateCryptoSuggestions } from "@/components/SmartSuggestions";
import { Target, Search, Filter } from "lucide-react";

interface Opportunity {
  id: string;
  buy_exchange: string;
  sell_exchange: string;
  symbol: string;
  buy_price: string;
  sell_price: string;
  gross_spread: string;
  gross_spread_percent: string;
  buy_fee: string;
  sell_fee: string;
  estimated_slippage: string;
  total_cost: string;
  gross_profit: string;
  net_profit: string;
  net_profit_percent: string;
  quantity: string;
  status: string;
  rejection_reason: string | null;
  rejection_details: string | null;
  created_at: string;
}

export default function OpportunitiesPage() {
  const [opportunities, setOpportunities] = useState<Opportunity[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [filter, setFilter] = useState("all");
  const [expanded, setExpanded] = useState<string | null>(null);

  useEffect(() => {
    const load = async () => {
      try {
        // Try demo endpoint first, fallback to regular
        let data;
        try {
          data = await api.demoOpportunities();
        } catch {
          data = await api.opportunities();
        }
        setOpportunities((data.opportunities as Opportunity[]) || []);
      } catch {}
      setLoading(false);
    };
    load();
    const interval = setInterval(load, 3000);
    return () => clearInterval(interval);
  }, []);

  const filtered = opportunities.filter((o) => {
    if (search && !o.symbol.toLowerCase().includes(search.toLowerCase())) return false;
    if (filter === "executable" && o.status !== "executable") return false;
    if (filter === "rejected" && o.status !== "rejected") return false;
    return true;
  });

  return (
    <DashboardLayout>
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-white">Opportunities</h1>
            <p className="text-sm text-slate-400 mt-1">Detected arbitrage opportunities</p>
          </div>
          <div className="flex items-center gap-3">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
              <input
                type="text"
                placeholder="Search symbol..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                className="pl-9 pr-4 py-2 rounded-lg bg-dark-700 border border-dark-600 text-sm text-white placeholder-slate-500 focus:outline-none focus:border-accent w-48"
              />
            </div>
            <select
              value={filter}
              onChange={(e) => setFilter(e.target.value)}
              className="px-3 py-2 rounded-lg bg-dark-700 border border-dark-600 text-sm text-white focus:outline-none focus:border-accent"
            >
              <option value="all">All</option>
              <option value="executable">Executable</option>
              <option value="rejected">Rejected</option>
            </select>
          </div>
        </div>

        <SmartSuggestions suggestions={generateCryptoSuggestions(opportunities)} title="Crypto Arbitrage Tips" />

        {loading ? (
          <div className="flex items-center justify-center h-64">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-accent" />
          </div>
        ) : filtered.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-64 text-slate-500">
            <Target className="w-12 h-12 mb-3 opacity-50" />
            <p className="text-lg font-medium">No opportunities found</p>
            <p className="text-sm">Opportunities will appear when price differences are detected</p>
          </div>
        ) : (
          <div className="overflow-x-auto rounded-xl border border-dark-600">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-dark-600 bg-dark-700/50">
                  <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wider text-slate-400">Pair</th>
                  <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wider text-slate-400">Buy Exchange</th>
                  <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wider text-slate-400">Sell Exchange</th>
                  <th className="px-4 py-3 text-right text-xs font-semibold uppercase tracking-wider text-slate-400">Buy Price</th>
                  <th className="px-4 py-3 text-right text-xs font-semibold uppercase tracking-wider text-slate-400">Sell Price</th>
                  <th className="px-4 py-3 text-right text-xs font-semibold uppercase tracking-wider text-slate-400">Spread</th>
                  <th className="px-4 py-3 text-right text-xs font-semibold uppercase tracking-wider text-slate-400">Net Profit</th>
                  <th className="px-4 py-3 text-center text-xs font-semibold uppercase tracking-wider text-slate-400">Status</th>
                  <th className="px-4 py-3 text-center text-xs font-semibold uppercase tracking-wider text-slate-400">Details</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-dark-600">
                {filtered.map((o) => (
                  <Fragment key={o.id}>
                    <tr className="hover:bg-dark-700/30 transition-colors">
                      <td className="px-4 py-3 font-semibold text-white">{o.symbol}</td>
                      <td className="px-4 py-3 text-slate-300">{o.buy_exchange}</td>
                      <td className="px-4 py-3 text-slate-300">{o.sell_exchange}</td>
                      <td className="px-4 py-3 text-right font-mono text-slate-300">₹{o.buy_price}</td>
                      <td className="px-4 py-3 text-right font-mono text-slate-300">₹{o.sell_price}</td>
                      <td className="px-4 py-3 text-right font-mono text-info">{o.gross_spread_percent}%</td>
                      <td className="px-4 py-3 text-right font-mono">
                        <span className={Number(o.net_profit) >= 0 ? "text-success" : "text-danger"}>
                          ₹{o.net_profit} ({o.net_profit_percent}%)
                        </span>
                      </td>
                      <td className="px-4 py-3 text-center">
                        <Badge variant={o.status === "executable" ? "success" : o.status === "rejected" ? "danger" : "neutral"}>
                          {o.status}
                        </Badge>
                      </td>
                      <td className="px-4 py-3 text-center">
                        <button
                          onClick={() => setExpanded(expanded === o.id ? null : o.id)}
                          className="text-xs text-accent hover:text-accent-hover transition-colors"
                        >
                          {expanded === o.id ? "Hide" : "View"}
                        </button>
                      </td>
                    </tr>
                    {expanded === o.id && (
                      <tr key={`${o.id}-detail`}>
                        <td colSpan={9} className="px-4 py-4 bg-dark-700/20">
                          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-xs">
                            <div><span className="text-slate-500">Buy Fee:</span> <span className="text-white font-mono">₹{o.buy_fee}</span></div>
                            <div><span className="text-slate-500">Sell Fee:</span> <span className="text-white font-mono">₹{o.sell_fee}</span></div>
                            <div><span className="text-slate-500">Slippage:</span> <span className="text-white font-mono">₹{o.estimated_slippage}</span></div>
                            <div><span className="text-slate-500">Total Cost:</span> <span className="text-white font-mono">₹{o.total_cost}</span></div>
                            <div><span className="text-slate-500">Quantity:</span> <span className="text-white font-mono">{o.quantity}</span></div>
                            <div><span className="text-slate-500">Gross Profit:</span> <span className="text-white font-mono">₹{o.gross_profit}</span></div>
                            {o.rejection_reason && (
                              <div className="col-span-2"><span className="text-slate-500">Rejection:</span> <span className="text-danger font-mono">{o.rejection_reason}</span></div>
                            )}
                            {o.rejection_details && (
                              <div className="col-span-2"><span className="text-slate-500">Details:</span> <span className="text-slate-300">{o.rejection_details}</span></div>
                            )}
                          </div>
                        </td>
                      </tr>
                    )}
                  </Fragment>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </DashboardLayout>
  );
}
