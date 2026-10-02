"use client";

import { useEffect, useState } from "react";
import DashboardLayout from "@/components/DashboardLayout";
import ChartCard from "@/components/ChartCard";
import { api } from "@/lib/api";
import { formatCurrency } from "@/lib/format";
import { Wallet, TrendingUp, TrendingDown } from "lucide-react";
import {
  AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer, BarChart, Bar, PieChart, Pie, Cell
} from "recharts";

interface PortfolioData {
  initial_capital: string;
  current_capital: string;
  total_pnl: string;
  total_trades: number;
  winning_trades: number;
  losing_trades: number;
  win_rate: string;
  max_drawdown: string;
}

export default function PortfolioPage() {
  const [portfolio, setPortfolio] = useState<PortfolioData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const load = async () => {
      try {
        let data: PortfolioData;
        try {
          const demo = await api.demoPortfolio();
          data = {
            initial_capital: demo.portfolio.initial_capital,
            current_capital: demo.portfolio.current_capital,
            total_pnl: demo.paper_trading.total_pnl,
            total_trades: Number(demo.paper_trading.total_trades),
            winning_trades: Number(demo.paper_trading.winning_trades),
            losing_trades: Number(demo.paper_trading.losing_trades),
            win_rate: demo.paper_trading.win_rate,
            max_drawdown: "0",
          };
        } catch {
          data = await api.portfolio();
        }
        setPortfolio(data);
      } catch {}
      setLoading(false);
    };
    load();
    const interval = setInterval(load, 3000);
    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return (
      <DashboardLayout>
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-accent" />
        </div>
      </DashboardLayout>
    );
  }

  const capitalData = [
    { name: "Initial", capital: Number(portfolio?.initial_capital || 10000) },
    { name: "Current", capital: Number(portfolio?.current_capital || 10000) },
  ];

  const performanceData = [
    { name: "Wins", value: portfolio?.winning_trades || 0, fill: "#22c55e" },
    { name: "Losses", value: portfolio?.losing_trades || 0, fill: "#ef4444" },
  ];

  const pnl = Number(portfolio?.total_pnl || 0);
  const winRate = Number(portfolio?.win_rate || 0);

  return (
    <DashboardLayout>
      <div className="space-y-6">
        <div>
          <h1 className="text-2xl font-bold text-white">Portfolio</h1>
          <p className="text-sm text-slate-400 mt-1">Capital and performance overview</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="rounded-xl border border-dark-600 bg-dark-800 p-5">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-lg bg-accent/20 flex items-center justify-center">
                <Wallet className="w-5 h-5 text-accent" />
              </div>
              <div>
                <p className="text-xs text-slate-400 uppercase">Initial Capital</p>
                <p className="text-xl font-bold text-white">{formatCurrency(portfolio?.initial_capital || "10000")}</p>
              </div>
            </div>
          </div>
          <div className="rounded-xl border border-dark-600 bg-dark-800 p-5">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-lg bg-success/20 flex items-center justify-center">
                <TrendingUp className="w-5 h-5 text-success" />
              </div>
              <div>
                <p className="text-xs text-slate-400 uppercase">Current Capital</p>
                <p className="text-xl font-bold text-white">{formatCurrency(portfolio?.current_capital || "10000")}</p>
              </div>
            </div>
          </div>
          <div className="rounded-xl border border-dark-600 bg-dark-800 p-5">
            <div className="flex items-center gap-3">
              <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${pnl >= 0 ? "bg-success/20" : "bg-danger/20"}`}>
                {pnl >= 0 ? <TrendingUp className="w-5 h-5 text-success" /> : <TrendingDown className="w-5 h-5 text-danger" />}
              </div>
              <div>
                <p className="text-xs text-slate-400 uppercase">Total P&L</p>
                <p className={`text-xl font-bold ${pnl >= 0 ? "text-success" : "text-danger"}`}>{formatCurrency(portfolio?.total_pnl || "0")}</p>
              </div>
            </div>
          </div>
          <div className="rounded-xl border border-dark-600 bg-dark-800 p-5">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-lg bg-info/20 flex items-center justify-center">
                <span className="text-info text-lg font-bold">%</span>
              </div>
              <div>
                <p className="text-xs text-slate-400 uppercase">Win Rate</p>
                <p className="text-xl font-bold text-white">{portfolio?.win_rate}%</p>
              </div>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          <ChartCard title="Capital Curve">
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={capitalData}>
                  <defs>
                    <linearGradient id="capitalGrad" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3} />
                      <stop offset="95%" stopColor="#3b82f6" stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="#222240" />
                  <XAxis dataKey="name" stroke="#64748b" fontSize={12} />
                  <YAxis stroke="#64748b" fontSize={12} />
                  <Tooltip contentStyle={{ background: "#1a1a2e", border: "1px solid #222240", borderRadius: "8px", color: "#e2e8f0" }} />
                  <Area type="monotone" dataKey="capital" stroke="#3b82f6" fillOpacity={1} fill="url(#capitalGrad)" strokeWidth={2} />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </ChartCard>

          <ChartCard title="Win / Loss Distribution">
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={performanceData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#222240" />
                  <XAxis dataKey="name" stroke="#64748b" fontSize={12} />
                  <YAxis stroke="#64748b" fontSize={12} />
                  <Tooltip contentStyle={{ background: "#1a1a2e", border: "1px solid #222240", borderRadius: "8px", color: "#e2e8f0" }} />
                  <Bar dataKey="value" radius={[6, 6, 0, 0]}>
                    {performanceData.map((entry, index) => (
                      <Cell key={index} fill={entry.fill} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          </ChartCard>
        </div>

        <ChartCard title="Performance Summary">
          <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
            <StatBox label="Total Trades" value={String(portfolio?.total_trades || 0)} />
            <StatBox label="Winning" value={String(portfolio?.winning_trades || 0)} color="text-success" />
            <StatBox label="Losing" value={String(portfolio?.losing_trades || 0)} color="text-danger" />
            <StatBox label="Win Rate" value={`${portfolio?.win_rate || 0}%`} color="text-info" />
            <StatBox label="Max Drawdown" value={`${portfolio?.max_drawdown || 0}%`} color="text-warning" />
          </div>
        </ChartCard>
      </div>
    </DashboardLayout>
  );
}

function StatBox({ label, value, color }: { label: string; value: string; color?: string }) {
  return (
    <div className="text-center p-4 rounded-lg bg-dark-700/50 border border-dark-600">
      <p className="text-xs text-slate-400 uppercase mb-1">{label}</p>
      <p className={`text-lg font-bold ${color || "text-white"}`}>{value}</p>
    </div>
  );
}
