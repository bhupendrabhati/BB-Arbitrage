"use client";

import { useEffect, useState } from "react";
import DashboardLayout from "@/components/DashboardLayout";
import ChartCard from "@/components/ChartCard";
import Badge from "@/components/Badge";
import Modal from "@/components/Modal";
import { api } from "@/lib/api";
import { formatCurrency } from "@/lib/format";
import { Shield, AlertTriangle, Power } from "lucide-react";

interface RiskData {
  daily_pnl: string;
  daily_trades: number;
  open_trades: number;
  total_exposure: string;
  daily_loss_limit: string;
  max_open_trades: number;
  max_trades_per_day: number;
  kill_switch_active: boolean;
}

interface KillSwitchData {
  active: boolean;
  activated_at: string | null;
  reason: string;
}

export default function RiskPage() {
  const [risk, setRisk] = useState<RiskData | null>(null);
  const [killSwitch, setKillSwitch] = useState<KillSwitchData | null>(null);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [reason, setReason] = useState("");
  const [action, setAction] = useState<"activate" | "deactivate">("activate");

  const load = async () => {
    try {
      let r, ks;
      try {
        const demo = await api.demoPortfolio();
        r = {
          daily_pnl: demo.risk.daily_pnl,
          daily_trades: Number(demo.risk.daily_trades),
          open_trades: Number(demo.risk.open_trades),
          total_exposure: demo.risk.total_exposure,
          daily_loss_limit: "-2",
          max_open_trades: Number(demo.risk.max_open_trades),
          max_trades_per_day: Number(demo.risk.max_trades_per_day),
          kill_switch_active: demo.risk.kill_switch_active === "True",
        };
        ks = await api.killSwitch();
      } catch {
        [r, ks] = await Promise.all([api.riskStatus(), api.killSwitch()]);
      }
      setRisk(r);
      setKillSwitch(ks);
    } catch {}
    setLoading(false);
  };

  useEffect(() => { load(); }, []);

  const handleKillSwitch = async () => {
    try {
      if (action === "activate") {
        await api.activateKillSwitch(reason || "Manual activation");
      } else {
        await api.deactivateKillSwitch();
      }
      setShowModal(false);
      setReason("");
      load();
    } catch (e) {
      console.error(e);
    }
  };

  if (loading) {
    return (
      <DashboardLayout>
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-accent" />
        </div>
      </DashboardLayout>
    );
  }

  const dailyLossUsed = risk ? (Math.abs(Number(risk.daily_pnl)) / 500) * 100 : 0;
  const tradesUsed = risk ? (risk.daily_trades / risk.max_trades_per_day) * 100 : 0;
  const openUsed = risk ? (risk.open_trades / risk.max_open_trades) * 100 : 0;

  return (
    <DashboardLayout>
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-white">Risk Control</h1>
            <p className="text-sm text-slate-400 mt-1">Monitor and control trading risk</p>
          </div>
          <button
            onClick={() => { setAction(killSwitch?.active ? "deactivate" : "activate"); setShowModal(true); }}
            className={`flex items-center gap-2 px-5 py-2.5 rounded-lg text-sm font-semibold transition-all ${
              killSwitch?.active
                ? "bg-success/15 text-success border border-success/30 hover:bg-success/25"
                : "bg-danger/15 text-danger border border-danger/30 hover:bg-danger/25"
            }`}
          >
            <Power className="w-4 h-4" />
            {killSwitch?.active ? "Reset Kill Switch" : "Activate Kill Switch"}
          </button>
        </div>

        {killSwitch?.active && (
          <div className="rounded-xl border border-danger/30 bg-danger/10 p-4 flex items-center gap-3 animate-slide-in">
            <AlertTriangle className="w-5 h-5 text-danger" />
            <div>
              <p className="text-sm font-semibold text-danger">Kill Switch Active</p>
              <p className="text-xs text-slate-400">Reason: {killSwitch.reason} | Since: {killSwitch.activated_at ? new Date(killSwitch.activated_at).toLocaleString() : "N/A"}</p>
            </div>
          </div>
        )}

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <KPICard title="Daily P&L" value={formatCurrency(risk?.daily_pnl || "0")} limit={`Limit: ${formatCurrency(risk?.daily_loss_limit || "-500")}`} used={dailyLossUsed} color={dailyLossUsed > 80 ? "red" : "blue"} />
          <KPICard title="Trades Today" value={`${risk?.daily_trades || 0}`} limit={`Max: ${risk?.max_trades_per_day || 5}`} used={tradesUsed} color={tradesUsed > 80 ? "yellow" : "cyan"} />
          <KPICard title="Open Trades" value={`${risk?.open_trades || 0}`} limit={`Max: ${risk?.max_open_trades || 1}`} used={openUsed} color={openUsed > 80 ? "yellow" : "green"} />
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          <ChartCard title="Risk Limits">
            <div className="space-y-5">
              <RiskMeter label="Daily Loss Limit" used={dailyLossUsed} value={`${formatCurrency(risk?.daily_pnl || "0")} / ${formatCurrency(risk?.daily_loss_limit || "-500")}`} color="red" />
              <RiskMeter label="Max Trades Per Day" used={tradesUsed} value={`${risk?.daily_trades || 0} / ${risk?.max_trades_per_day || 5}`} color="cyan" />
              <RiskMeter label="Max Open Trades" used={openUsed} value={`${risk?.open_trades || 0} / ${risk?.max_open_trades || 1}`} color="green" />
              <RiskMeter label="Total Exposure" used={0} value={formatCurrency(risk?.total_exposure || "0")} color="blue" />
            </div>
          </ChartCard>

          <ChartCard title="System Status">
            <div className="space-y-3">
              <StatusRow label="Trading Mode" value={risk?.kill_switch_active ? "STOPPED" : "ACTIVE"} ok={!risk?.kill_switch_active} />
              <StatusRow label="Kill Switch" value={killSwitch?.active ? "ACTIVE" : "OFF"} ok={!killSwitch?.active} />
              <StatusRow label="Daily Loss OK" value={dailyLossUsed < 100 ? "YES" : "LIMIT REACHED"} ok={dailyLossUsed < 100} />
              <StatusRow label="Trade Limit OK" value={tradesUsed < 100 ? "YES" : "LIMIT REACHED"} ok={tradesUsed < 100} />
            </div>
          </ChartCard>
        </div>
      </div>

      <Modal
        open={showModal}
        onClose={() => setShowModal(false)}
        title={action === "activate" ? "Activate Kill Switch" : "Deactivate Kill Switch"}
        actions={
          <>
            <button onClick={() => setShowModal(false)} className="px-4 py-2 rounded-lg bg-dark-600 text-slate-300 text-sm hover:bg-dark-500 transition-colors">
              Cancel
            </button>
            <button
              onClick={handleKillSwitch}
              className={`px-4 py-2 rounded-lg text-sm font-semibold transition-colors ${
                action === "activate" ? "bg-danger text-white hover:bg-danger/80" : "bg-success text-white hover:bg-success/80"
              }`}
            >
              {action === "activate" ? "Activate" : "Deactivate"}
            </button>
          </>
        }
      >
        {action === "activate" ? (
          <div className="space-y-4">
            <p className="text-sm text-slate-400">This will stop all trading activity immediately.</p>
            <div>
              <label className="text-xs text-slate-400 block mb-1">Reason</label>
              <input
                type="text"
                value={reason}
                onChange={(e) => setReason(e.target.value)}
                placeholder="e.g., Abnormal market behavior"
                className="w-full px-3 py-2 rounded-lg bg-dark-700 border border-dark-600 text-sm text-white placeholder-slate-500 focus:outline-none focus:border-danger"
              />
            </div>
          </div>
        ) : (
          <p className="text-sm text-slate-400">This will re-enable trading. Make sure market conditions are normal.</p>
        )}
      </Modal>
    </DashboardLayout>
  );
}

function KPICard({ title, value, limit, used, color }: { title: string; value: string; limit: string; used: number; color: string }) {
  const colorMap: Record<string, string> = {
    red: "bg-danger",
    cyan: "bg-info",
    green: "bg-success",
    yellow: "bg-warning",
    blue: "bg-accent",
  };

  return (
    <div className="rounded-xl border border-dark-600 bg-dark-800 p-5">
      <p className="text-xs text-slate-400 uppercase mb-1">{title}</p>
      <p className="text-2xl font-bold text-white">{value}</p>
      <p className="text-xs text-slate-500 mt-1">{limit}</p>
      <div className="mt-3 h-1.5 bg-dark-600 rounded-full overflow-hidden">
        <div className={`h-full rounded-full transition-all duration-500 ${colorMap[color]}`} style={{ width: `${Math.min(used, 100)}%` }} />
      </div>
    </div>
  );
}

function RiskMeter({ label, used, value, color }: { label: string; used: number; value: string; color: string }) {
  const colorMap: Record<string, string> = {
    red: "bg-danger",
    cyan: "bg-info",
    green: "bg-success",
    yellow: "bg-warning",
    blue: "bg-accent",
  };

  return (
    <div>
      <div className="flex justify-between text-sm mb-1.5">
        <span className="text-slate-400">{label}</span>
        <span className="text-slate-300 font-mono text-xs">{value}</span>
      </div>
      <div className="h-2.5 bg-dark-600 rounded-full overflow-hidden">
        <div className={`h-full rounded-full transition-all duration-700 ${colorMap[color]}`} style={{ width: `${Math.min(used, 100)}%` }} />
      </div>
    </div>
  );
}

function StatusRow({ label, value, ok }: { label: string; value: string; ok: boolean }) {
  return (
    <div className="flex items-center justify-between p-3 rounded-lg bg-dark-700/50 border border-dark-600">
      <span className="text-sm text-slate-400">{label}</span>
      <div className="flex items-center gap-2">
        <div className={`w-2 h-2 rounded-full ${ok ? "bg-success" : "bg-danger animate-pulse"}`} />
        <span className={`text-sm font-semibold ${ok ? "text-success" : "text-danger"}`}>{value}</span>
      </div>
    </div>
  );
}
