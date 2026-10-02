"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { clsx } from "clsx";
import {
  LayoutDashboard,
  Target,
  ArrowLeftRight,
  Wallet,
  Shield,
  FlaskConical,
  Activity,
  Zap,
  TrendingUp,
  BarChart3,
} from "lucide-react";

const links = [
  { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { href: "/opportunities", label: "Crypto Arb", icon: Target },
  { href: "/stocks", label: "Stocks", icon: TrendingUp },
  { href: "/fno", label: "F&O Options", icon: BarChart3 },
  { href: "/trades", label: "Trades", icon: ArrowLeftRight },
  { href: "/portfolio", label: "Portfolio", icon: Wallet },
  { href: "/risk", label: "Risk Control", icon: Shield },
  { href: "/backtesting", label: "Backtesting", icon: FlaskConical },
];

export default function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="fixed left-0 top-0 z-40 h-screen w-64 border-r border-dark-600 bg-dark-800 flex flex-col">
      <div className="flex items-center gap-3 px-6 py-5 border-b border-dark-600">
        <div className="w-9 h-9 rounded-lg bg-accent/20 flex items-center justify-center">
          <Zap className="w-5 h-5 text-accent" />
        </div>
        <div>
          <h1 className="text-base font-bold text-white tracking-tight">BB-ARBITRAGE</h1>
          <p className="text-[10px] text-slate-500 uppercase tracking-widest">v1.0.0</p>
        </div>
      </div>

      <nav className="flex-1 px-3 py-4 space-y-1">
        {links.map((link) => {
          const active = pathname === link.href;
          return (
            <Link
              key={link.href}
              href={link.href}
              className={clsx(
                "flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all duration-200",
                active
                  ? "bg-accent/15 text-accent border border-accent/30"
                  : "text-slate-400 hover:text-white hover:bg-dark-700 border border-transparent"
              )}
            >
              <link.icon className={clsx("w-4 h-4", active && "text-accent")} />
              {link.label}
            </Link>
          );
        })}
      </nav>

      <div className="px-4 py-4 border-t border-dark-600">
        <div className="flex items-center gap-2 text-xs text-slate-500">
          <Activity className="w-3 h-3 text-success" />
          <span>System Online</span>
        </div>
      </div>
    </aside>
  );
}
