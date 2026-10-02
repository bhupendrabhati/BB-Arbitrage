"use client";

import { useEffect, useState } from "react";
import DashboardLayout from "@/components/DashboardLayout";
import KPICard from "@/components/KPICard";
import ChartCard from "@/components/ChartCard";
import { api } from "@/lib/api";
import { formatCurrency, formatPercent } from "@/lib/format";
import {
  Wallet, TrendingUp, Target, Shield, Zap, Play, Loader2
} from "lucide-react";
import {
  AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer, PieChart, Pie, Cell
} from "recharts";

export default function DashboardPage() {
  const [demoStarted, setDemoStarted] = useState(false);
  const [loading, setLoading] = useState(true);
  const [portfolio, setPortfolio] = useState<{ capital: string; initial_capital: string; total_pnl: string; total_trades: number; winning_trades: number; losing_trades: number; win_rate: string } | null>(null);
  const [risk, setRisk] = useState<{ daily_pnl: string; kill_switch_active: boolean; daily_trades: number; max_trades_per_day: number; open_trades: number; max_open_trades: number } | null>(null);
  const [oppCount, setOppCount] = useState({ total: 0, executable: 0 });
  const [capHistory, setCapHistory] = useState<{ name: string; value: number }[]>([]);
  const [health, setHealth] = useState<{ mode: string; live_trading_enabled: boolean; kill_switch_active: boolean } | null>(null);

  const startDemo = async () => {
    try {
      await api.startDemo();
      setDemoStarted(true);
    } catch (e) {
      console.error(e);
    }
  };

  useEffect(() => {
    const load = async () => {
      try {
        const [h, demo] = await Promise.all([api.health(), api.demoPortfolio()]);
        setHealth(h);
        setPortfolio({
          capital: demo.paper_trading.capital,
          initial_capital: demo.paper_trading.initial_capital ?? "0",
          total_pnl: demo.paper_trading.total_pnl,
          total_trades: Number(demo.paper_trading.total_trades),
          winning_trades: Number(demo.paper_trading.winning_trades),
          losing_trades: Number(demo.paper_trading.losing_trades),
          win_rate: demo.paper_trading.win_rate,
        });
        setRisk({
          daily_pnl: demo.risk.daily_pnl,
          kill_switch_active: demo.risk.kill_switch_active === "True",
          daily_trades: Number(demo.risk.daily_trades),
          max_trades_per_day: Number(demo.risk.max_trades_per_day),
          open_trades: Number(demo.risk.open_trades),
          max_open_trades: Number(demo.risk.max_open_trades),
        });

        try {
          const opps = await api.demoOpportunities();
          const all = (opps.opportunities || []) as Record<string, unknown>[];
          setOppCount({
            total: all.length,
            executable: all.filter((o) => o.status === "executable").length,
          });
        } catch {}

        // Track capital history
        setCapHistory(prev => {
          const newVal = { name: String(prev.length), value: Number(demo.paper_trading.capital) };
          const updated = [...prev, newVal];
          return updated.slice(-20);
        });
      } catch {}
      setLoading(false);
    };

    load();
    const interval = setInterval(load, 3000);
    return () => clearInterval(interval);
  }, [demoStarted]);

  if (loading && !demoStarted) {
    return (
      <DashboardLayout>
        <div className="flex flex-col items-center justify-center h-[60vh] space-y-6">
          <div className="w-20 h-20 rounded-2xl bg-accent/20 flex items-center justify-center">
            <Zap className="w-10 h-10 text-accent" />
          </div>
          <div className="text-center">
            <h1 className="text-3xl font-bold text-white mb-2">BB-ARBITRAGE</h1>
            <p className="text-slate-400">Crypto Arbitrage Research Platform</p>
          </div>
          <button
            onClick={startDemo}
            className="flex items-center gap-3 px-8 py-4 rounded-xl bg-accent text-white text-lg font-semibold hover:bg-accent-hover transition-all hover:scale-105 animate-pulse-glow"
          >
            <Play className="w-5 h-5" />
            Start Demo Mode
          </button>
          <p className="text-xs text-slate-500">Simulates 3 exchanges with realistic price data</p>
        </div>
      </DashboardLayout>
    );
  }

  if (loading) {
    return (
      <DashboardLayout>
        <div className="flex items-center justify-center h-64">
          <Loader2 className="w-8 h-8 text-accent animate-spin" />
        </div>
      </DashboardLayout>
    );
  }

  const pnl = Number(portfolio?.total_pnl || 0);
  const COLORS = ["#22c55e", "#ef4444"];
  const winLossData = [
    { name: "Wins", value: portfolio?.winning_trades || 0 },
    { name: "Losses", value: portfolio?.losing_trades || 0 },
  ];

  return (
    <DashboardLayout>
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-white">Dashboard</h1>
            <p className="text-sm text-slate-400 mt-1">Real-time market analysis</p>
          </div>
          <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-success/15 border border-success/30">
            <div className="w-2 h-2 rounded-full bg-success animate-pulse" />
            <span className="text-xs font-medium text-success">DEMO RUNNING</span>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <KPICard
            title="Capital"
            value={formatCurrency(portfolio?.capital || "10000")}
            subtitle={`Starting: ${formatCurrency(portfolio?.initial_capital || "10000")}`}
            icon={<Wallet className="w-5 h-5" />}
            color="blue"
          />
          <KPICard
            title="Total P&L"
            value={formatCurrency(portfolio?.total_pnl || "0")}
            subtitle={`${portfolio?.total_trades || 0} trades executed`}
            icon={<TrendingUp className="w-5 h-5" />}
            color={pnl >= 0 ? "green" : "red"}
            trend={pnl >= 0 ? "up" : "down"}
            trendValue={`${portfolio?.win_rate || "0"}% win rate`}
          />
          <KPICard
            title="Opportunities"
            value={oppCount.total}
            subtitle={`${oppCount.executable} executable`}
            icon={<Target className="w-5 h-5" />}
            color="cyan"
          />
          <KPICard
            title="Risk"
            value={risk?.kill_switch_active ? "STOPPED" : "OK"}
            subtitle={`Trades today: ${risk?.daily_trades || 0}/${risk?.max_trades_per_day || 5}`}
            icon={<Shield className="w-5 h-5" />}
            color={risk?.kill_switch_active ? "red" : "green"}
          />
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
          <ChartCard title="Capital Curve" action={<span className="text-xs text-slate-500">Last 20 updates</span>}>
            <div className="h-56">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={capHistory}>
                  <defs>
                    <linearGradient id="colorValue" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3} />
                      <stop offset="95%" stopColor="#3b82f6" stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="#222240" />
                  <XAxis dataKey="name" stroke="#64748b" fontSize={10} />
                  <YAxis stroke="#64748b" fontSize={10} />
                  <Tooltip contentStyle={{ background: "#1a1a2e", border: "1px solid #222240", borderRadius: "8px", color: "#e2e8f0" }} />
                  <Area type="monotone" dataKey="value" stroke="#3b82f6" fillOpacity={1} fill="url(#colorValue)" strokeWidth={2} />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </ChartCard>

          <ChartCard title="Win / Loss">
            <div className="h-48">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie data={winLossData} cx="50%" cy="50%" innerRadius={45} outerRadius={65} paddingAngle={4} dataKey="value">
                    {winLossData.map((_, index) => (
                      <Cell key={index} fill={COLORS[index]} />
                    ))}
                  </Pie>
                  <Tooltip contentStyle={{ background: "#1a1a2e", border: "1px solid #222240", borderRadius: "8px", color: "#e2e8f0" }} />
                </PieChart>
              </ResponsiveContainer>
            </div>
            <div className="flex justify-center gap-6 text-xs">
              <span className="flex items-center gap-1.5"><span className="w-2 h-2 rounded-full bg-success" /> Wins: {portfolio?.winning_trades || 0}</span>
              <span className="flex items-center gap-1.5"><span className="w-2 h-2 rounded-full bg-danger" /> Losses: {portfolio?.losing_trades || 0}</span>
            </div>
          </ChartCard>

          <ChartCard title="System Status">
            <div className="space-y-3">
              <StatusRow label="Mode" value={health?.mode?.toUpperCase() || "PAPER"} ok />
              <StatusRow label="Live Trading" value="OFF" ok />
              <StatusRow label="Kill Switch" value={risk?.kill_switch_active ? "ACTIVE" : "OFF"} ok={!risk?.kill_switch_active} />
              <StatusRow label="Exchanges" value="3 Connected" ok />
              <StatusRow label="Data Feed" value="Real-time" ok />
            </div>
          </ChartCard>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          <ChartCard title="Risk Limits">
            <div className="space-y-4">
              <RiskBar label="Daily Trades" used={risk ? (risk.daily_trades / risk.max_trades_per_day) * 100 : 0} current={risk?.daily_trades || 0} max={risk?.max_trades_per_day || 5} color="blue" />
              <RiskBar label="Open Trades" used={risk ? (risk.open_trades / risk.max_open_trades) * 100 : 0} current={risk?.open_trades || 0} max={risk?.max_open_trades || 1} color="cyan" />
              <RiskBar label="Daily P&L" used={risk ? (Math.abs(Number(risk.daily_pnl)) / 500) * 100 : 0} current={formatCurrency(risk?.daily_pnl || "0")} max={`${formatCurrency(500)} limit`} color="red" />
            </div>
          </ChartCard>

          <ChartCard title="How It Works">
            <div className="space-y-3 text-sm">
              <div className="flex items-start gap-3">
                <span className="w-6 h-6 rounded-full bg-accent/20 text-accent flex items-center justify-center text-xs font-bold flex-shrink-0">1</span>
                <p className="text-slate-300">Collects real-time prices from <span className="text-white font-medium">3 simulated exchanges</span></p>
              </div>
              <div className="flex items-start gap-3">
                <span className="w-6 h-6 rounded-full bg-accent/20 text-accent flex items-center justify-center text-xs font-bold flex-shrink-0">2</span>
                <p className="text-slate-300">Compares prices to find <span className="text-white font-medium">arbitrage opportunities</span></p>
              </div>
              <div className="flex items-start gap-3">
                <span className="w-6 h-6 rounded-full bg-accent/20 text-accent flex items-center justify-center text-xs font-bold flex-shrink-0">3</span>
                <p className="text-slate-300">Calculates <span className="text-white font-medium">net profit after fees, slippage, costs</span></p>
              </div>
              <div className="flex items-start gap-3">
                <span className="w-6 h-6 rounded-full bg-accent/20 text-accent flex items-center justify-center text-xs font-bold flex-shrink-0">4</span>
                <p className="text-slate-300">Executes <span className="text-white font-medium">paper trades</span> automatically</p>
              </div>
              <div className="flex items-start gap-3">
                <span className="w-6 h-6 rounded-full bg-accent/20 text-accent flex items-center justify-center text-xs font-bold flex-shrink-0">5</span>
                <p className="text-slate-300">Tracks <span className="text-white font-medium">P&L, win rate, drawdown</span> in real-time</p>
              </div>
            </div>
          </ChartCard>
        </div>
      </div>
    </DashboardLayout>
  );
}

function StatusRow({ label, value, ok }: { label: string; value: string; ok: boolean }) {
  return (
    <div className="flex items-center justify-between p-2.5 rounded-lg bg-dark-700/50 border border-dark-600">
      <span className="text-xs text-slate-400">{label}</span>
      <div className="flex items-center gap-2">
        <div className={`w-1.5 h-1.5 rounded-full ${ok ? "bg-success" : "bg-danger animate-pulse"}`} />
        <span className={`text-xs font-semibold ${ok ? "text-success" : "text-danger"}`}>{value}</span>
      </div>
    </div>
  );
}

function RiskBar({ label, used, current, max, color }: { label: string; used: number; current: number | string; max: number | string; color: string }) {
  const colorMap: Record<string, string> = { red: "bg-danger", blue: "bg-accent", cyan: "bg-info", green: "bg-success", yellow: "bg-warning" };
  return (
    <div>
      <div className="flex justify-between text-xs mb-1.5">
        <span className="text-slate-400">{label}</span>
        <span className="text-slate-300 font-mono">{current} / {max}</span>
      </div>
      <div className="h-2 bg-dark-600 rounded-full overflow-hidden">
        <div className={`h-full rounded-full transition-all duration-500 ${colorMap[color]}`} style={{ width: `${Math.min(used, 100)}%` }} />
      </div>
    </div>
  );
}
