"use client";

import { RefreshCw, Bell } from "lucide-react";
import { useState, useEffect } from "react";
import { api } from "@/lib/api";

export default function Navbar() {
  const [mode, setMode] = useState("paper");
  const [killActive, setKillActive] = useState(false);
  const [now, setNow] = useState("");

  useEffect(() => {
    const load = async () => {
      try {
        const [health, ks] = await Promise.all([api.health(), api.killSwitch()]);
        setMode(health.mode);
        setKillActive(ks.active);
      } catch {}
    };
    load();
    const interval = setInterval(() => {
      setNow(new Date().toLocaleTimeString());
    }, 1000);
    return () => clearInterval(interval);
  }, []);

  return (
    <header className="sticky top-0 z-30 h-14 border-b border-dark-600 bg-dark-800/80 backdrop-blur-xl flex items-center justify-between px-6">
      <div className="flex items-center gap-4">
        <div className="flex items-center gap-2">
          <div className={`w-2 h-2 rounded-full ${killActive ? "bg-danger animate-pulse" : "bg-success"}`} />
          <span className="text-xs font-medium uppercase tracking-wider text-slate-400">
            {killActive ? "KILL SWITCH ACTIVE" : "LIVE"}
          </span>
        </div>
        <span className="text-xs px-2 py-1 rounded bg-dark-600 text-slate-300 font-mono uppercase">
          {mode} mode
        </span>
      </div>

      <div className="flex items-center gap-4">
        <span className="text-xs text-slate-500 font-mono">{now}</span>
        <button className="p-2 rounded-lg hover:bg-dark-700 text-slate-400 hover:text-white transition-colors">
          <Bell className="w-4 h-4" />
        </button>
        <button className="p-2 rounded-lg hover:bg-dark-700 text-slate-400 hover:text-white transition-colors">
          <RefreshCw className="w-4 h-4" />
        </button>
      </div>
    </header>
  );
}
