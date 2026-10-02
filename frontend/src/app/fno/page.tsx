"use client";

import { useEffect, useState } from "react";
import DashboardLayout from "@/components/DashboardLayout";
import Badge from "@/components/Badge";
import ChartCard from "@/components/ChartCard";
import SmartSuggestions, { generateFnOSuggestions } from "@/components/SmartSuggestions";
import { api } from "@/lib/api";
import { formatCurrency } from "@/lib/format";
import { BarChart3, Search, Loader2, TrendingUp, TrendingDown, ChevronDown, ChevronUp, Calculator } from "lucide-react";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, ReferenceLine, AreaChart, Area } from "recharts";

interface OptionContract {
  strike: number;
  last_price: number;
  bid: number;
  ask: number;
  volume: number;
  open_interest: number;
  implied_volatility: number;
  delta: number;
  gamma: number;
  theta: number;
  vega: number;
  in_the_money: boolean;
}

interface OptionChainData {
  symbol: string;
  current_price: number;
  expiry_dates: string[];
  selected_expiry: string;
  strikes: number[];
  calls: OptionContract[];
  puts: OptionContract[];
}

interface Strategy {
  name: string;
  description: string;
  legs: number;
  risk: string;
  reward: string;
}

interface StrategyResult {
  name: string;
  description: string;
  max_profit: number;
  max_loss: number;
  breakeven: number[];
  margin_required: number;
  risk_reward_ratio: number | null;
  pnl_at_expiry: { price: number; pnl: number }[];
  legs: { option_type: string; action: string; strike: number; expiry: string; quantity: number; premium: number }[];
}

const INDIAN_FNO = [
  { symbol: "NIFTY", name: "NIFTY 50", spot: 24500, type: "index" },
  { symbol: "BANKNIFTY", name: "BANK NIFTY", spot: 51200, type: "index" },
  { symbol: "RELIANCE", name: "Reliance", spot: 1250, type: "stock" },
  { symbol: "TCS", name: "TCS", spot: 2090, type: "stock" },
  { symbol: "INFY", name: "Infosys", spot: 1020, type: "stock" },
  { symbol: "SBIN", name: "SBI", spot: 994, type: "stock" },
  { symbol: "HDFCBANK", name: "HDFC Bank", spot: 1700, type: "stock" },
];

const US_OPTIONS = ["AAPL", "MSFT", "TSLA", "NVDA", "AMD", "AMZN", "GOOGL", "META"];

export default function FnOPage() {
  const [market, setMarket] = useState<"indian" | "us">("indian");
  const [symbol, setSymbol] = useState("NIFTY");
  const [chain, setChain] = useState<OptionChainData | null>(null);
  const [loading, setLoading] = useState(false);
  const [selectedExpiry, setSelectedExpiry] = useState<string>("");
  const [showGreeks, setShowGreeks] = useState(false);
  const [activeTab, setActiveTab] = useState<"chain" | "strategy" | "pnl">("chain");

  const [strategies, setStrategies] = useState<Strategy[]>([]);
  const [selectedStrategy, setSelectedStrategy] = useState<string>("straddle");
  const [strategyLegs, setStrategyLegs] = useState<{ option_type: string; action: string; strike: number; premium: number; quantity: number }[]>([
    { option_type: "call", action: "buy", strike: 0, premium: 0, quantity: 1 },
  ]);
  const [strategyResult, setStrategyResult] = useState<StrategyResult | null>(null);
  const [calculating, setCalculating] = useState(false);

  useEffect(() => {
    api.optionStrategies().then(d => setStrategies(d)).catch(() => {});
  }, []);

  const fetchChain = async (sym: string, mkt: string, exp?: string) => {
    setLoading(true);
    try {
      const data = await api.optionChain(sym, mkt, exp);
      setChain(data);
      if (data.expiry_dates?.length && !exp) {
        setSelectedExpiry(data.expiry_dates[0]);
      }
    } catch {
      setChain(null);
    }
    setLoading(false);
  };

  useEffect(() => {
    fetchChain(symbol, market);
  }, [symbol, market]);

  const changeExpiry = (exp: string) => {
    setSelectedExpiry(exp);
    fetchChain(symbol, market, exp);
  };

  const calculateStrategy = async () => {
    if (!chain) return;
    setCalculating(true);
    try {
      const legs = strategyLegs.map(l => ({
        ...l,
        expiry: chain.selected_expiry,
      }));
      const result = await api.calculateStrategy({
        name: selectedStrategy,
        symbol: chain.symbol,
        spot: chain.current_price,
        legs,
      });
      setStrategyResult(result);
    } catch {}
    setCalculating(false);
  };

  const addLeg = () => {
    setStrategyLegs([...strategyLegs, { option_type: "call", action: "buy", strike: chain?.current_price || 0, premium: 0, quantity: 1 }]);
  };

  const removeLeg = (i: number) => {
    setStrategyLegs(strategyLegs.filter((_, idx) => idx !== i));
  };

  const updateLeg = (i: number, field: string, value: string | number) => {
    const updated = [...strategyLegs];
    (updated[i] as Record<string, unknown>)[field] = value;
    if (field === "strike" && chain) {
      const call = chain.calls.find(c => c.strike === Number(value));
      const put = chain.puts.find(p => p.strike === Number(value));
      if (updated[i].option_type === "call" && call) updated[i].premium = call.last_price;
      else if (updated[i].option_type === "put" && put) updated[i].premium = put.last_price;
    }
    setStrategyLegs(updated);
  };

  const itmCalls = chain?.calls.filter(c => c.in_the_money).length || 0;
  const otmCalls = chain?.calls.filter(c => !c.in_the_money).length || 0;
  const itmPuts = chain?.puts.filter(p => p.in_the_money).length || 0;
  const otmPuts = chain?.puts.filter(p => !p.in_the_money).length || 0;

  return (
    <DashboardLayout>
      <div className="space-y-6">
        <div>
          <h1 className="text-2xl font-bold text-white">F&O Options</h1>
          <p className="text-sm text-slate-400 mt-1">Options chain, Greeks, and strategy builder</p>
        </div>

        {/* Market Selector */}
        <div className="flex items-center gap-4 p-4 rounded-xl border border-dark-600 bg-dark-800">
          <span className="text-sm text-slate-400">Market:</span>
          {(["indian", "us"] as const).map(m => (
            <button key={m} onClick={() => { setMarket(m); setSymbol(m === "indian" ? "NIFTY" : "AAPL"); }}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${market === m ? "bg-accent/15 text-accent border border-accent/30" : "bg-dark-700 text-slate-400 border border-dark-600 hover:text-white"}`}>
              {m === "indian" ? "🇮🇳 Indian F&O" : "🇺🇸 US Options"}
            </button>
          ))}
        </div>

        <SmartSuggestions suggestions={generateFnOSuggestions(chain, selectedStrategy)} title="F&O Trading Guide" />

        {/* Symbol Selector */}
        <div className="flex flex-wrap gap-2">
          {market === "indian" ? INDIAN_FNO.map(s => (
            <button key={s.symbol} onClick={() => setSymbol(s.symbol)}
              className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all ${symbol === s.symbol ? "bg-accent/15 text-accent border border-accent/30" : "bg-dark-700 text-slate-400 border border-dark-600 hover:text-white"}`}>
              {s.name}
              <Badge variant={s.type === "index" ? "info" : "purple"}>{s.type}</Badge>
            </button>
          )) : US_OPTIONS.map(s => (
            <button key={s} onClick={() => setSymbol(s)}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${symbol === s ? "bg-accent/15 text-accent border border-accent/30" : "bg-dark-700 text-slate-400 border border-dark-600 hover:text-white"}`}>
              {s}
            </button>
          ))}
        </div>

        {/* Tabs */}
        <div className="flex gap-2">
          {(["chain", "strategy", "pnl"] as const).map(tab => (
            <button key={tab} onClick={() => setActiveTab(tab)}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${activeTab === tab ? "bg-accent/15 text-accent border border-accent/30" : "bg-dark-700 text-slate-400 border border-dark-600"}`}>
              {tab === "chain" ? "Options Chain" : tab === "strategy" ? "Strategy Builder" : "P&L Calculator"}
            </button>
          ))}
        </div>

        {/* Options Chain Tab */}
        {activeTab === "chain" && chain && (
          <div className="space-y-4">
            <div className="flex items-center gap-4 p-4 rounded-xl border border-dark-600 bg-dark-800">
              <div>
                <span className="text-xs text-slate-400 uppercase">Spot Price</span>
                <p className="text-xl font-bold text-white">{formatCurrency(chain.current_price, "₹")}</p>
              </div>
              <div className="flex-1" />
              <div>
                <span className="text-xs text-slate-400 uppercase">Expiry</span>
                <div className="flex gap-1 mt-1">
                  {chain.expiry_dates.map(exp => (
                    <button key={exp} onClick={() => changeExpiry(exp)}
                      className={`px-3 py-1 rounded text-xs font-medium ${selectedExpiry === exp ? "bg-accent text-white" : "bg-dark-700 text-slate-400 hover:text-white"}`}>
                      {exp}
                    </button>
                  ))}
                </div>
              </div>
              <button onClick={() => setShowGreeks(!showGreeks)}
                className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${showGreeks ? "bg-accent/15 text-accent border border-accent/30" : "bg-dark-700 text-slate-400 border border-dark-600"}`}>
                {showGreeks ? "Hide" : "Show"} Greeks
              </button>
            </div>

            {/* Summary badges */}
            <div className="flex gap-3">
              <Badge variant="success">ITM Calls: {itmCalls}</Badge>
              <Badge variant="warning">OTM Calls: {otmCalls}</Badge>
              <Badge variant="danger">ITM Puts: {itmPuts}</Badge>
              <Badge variant="info">OTM Puts: {otmPuts}</Badge>
            </div>

            {/* Options Chain Table */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
              {/* Calls */}
              <ChartCard title="CALLS">
                <div className="overflow-x-auto max-h-96 overflow-y-auto">
                  <table className="w-full text-xs">
                    <thead className="sticky top-0 bg-dark-800">
                      <tr className="border-b border-dark-600">
                        <th className="px-2 py-2 text-left text-slate-400">OI</th>
                        <th className="px-2 py-2 text-right text-slate-400">Volume</th>
                        <th className="px-2 py-2 text-right text-slate-400">IV</th>
                        <th className="px-2 py-2 text-right text-slate-400">LTP</th>
                        <th className="px-2 py-2 text-right text-slate-400">Bid</th>
                        <th className="px-2 py-2 text-right text-slate-400">Ask</th>
                        {showGreeks && <>
                          <th className="px-2 py-2 text-right text-slate-400">Delta</th>
                          <th className="px-2 py-2 text-right text-slate-400">Gamma</th>
                          <th className="px-2 py-2 text-right text-slate-400">Theta</th>
                          <th className="px-2 py-2 text-right text-slate-400">Vega</th>
                        </>}
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-dark-600">
                      {chain.calls.map((c, i) => (
                        <tr key={`call-${i}`} className={`hover:bg-dark-700/50 ${c.in_the_money ? "bg-success/5" : ""}`}>
                          <td className="px-2 py-2 font-mono text-slate-300">{(c.open_interest / 1000).toFixed(0)}K</td>
                          <td className="px-2 py-2 text-right font-mono text-slate-300">{(c.volume / 1000).toFixed(1)}K</td>
                          <td className="px-2 py-2 text-right font-mono text-warning">{(c.implied_volatility * 100).toFixed(1)}%</td>
                          <td className="px-2 py-2 text-right font-mono font-semibold text-white">{c.last_price.toFixed(2)}</td>
                          <td className="px-2 py-2 text-right font-mono text-slate-300">{c.bid.toFixed(2)}</td>
                          <td className="px-2 py-2 text-right font-mono text-slate-300">{c.ask.toFixed(2)}</td>
                          {showGreeks && <>
                            <td className="px-2 py-2 text-right font-mono text-accent">{c.delta.toFixed(3)}</td>
                            <td className="px-2 py-2 text-right font-mono text-slate-300">{c.gamma.toFixed(4)}</td>
                            <td className="px-2 py-2 text-right font-mono text-danger">{c.theta.toFixed(3)}</td>
                            <td className="px-2 py-2 text-right font-mono text-info">{c.vega.toFixed(3)}</td>
                          </>}
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </ChartCard>

              {/* Puts */}
              <ChartCard title="PUTS">
                <div className="overflow-x-auto max-h-96 overflow-y-auto">
                  <table className="w-full text-xs">
                    <thead className="sticky top-0 bg-dark-800">
                      <tr className="border-b border-dark-600">
                        {showGreeks && <>
                          <th className="px-2 py-2 text-left text-slate-400">Delta</th>
                          <th className="px-2 py-2 text-right text-slate-400">Gamma</th>
                          <th className="px-2 py-2 text-right text-slate-400">Theta</th>
                          <th className="px-2 py-2 text-right text-slate-400">Vega</th>
                        </>}
                        <th className="px-2 py-2 text-right text-slate-400">IV</th>
                        <th className="px-2 py-2 text-right text-slate-400">LTP</th>
                        <th className="px-2 py-2 text-right text-slate-400">Bid</th>
                        <th className="px-2 py-2 text-right text-slate-400">Ask</th>
                        <th className="px-2 py-2 text-right text-slate-400">Volume</th>
                        <th className="px-2 py-2 text-right text-slate-400">OI</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-dark-600">
                      {chain.puts.map((p, i) => (
                        <tr key={`put-${i}`} className={`hover:bg-dark-700/50 ${p.in_the_money ? "bg-danger/5" : ""}`}>
                          {showGreeks && <>
                            <td className="px-2 py-2 text-right font-mono text-accent">{p.delta.toFixed(3)}</td>
                            <td className="px-2 py-2 text-right font-mono text-slate-300">{p.gamma.toFixed(4)}</td>
                            <td className="px-2 py-2 text-right font-mono text-danger">{p.theta.toFixed(3)}</td>
                            <td className="px-2 py-2 text-right font-mono text-info">{p.vega.toFixed(3)}</td>
                          </>}
                          <td className="px-2 py-2 text-right font-mono text-warning">{(p.implied_volatility * 100).toFixed(1)}%</td>
                          <td className="px-2 py-2 text-right font-mono font-semibold text-white">{p.last_price.toFixed(2)}</td>
                          <td className="px-2 py-2 text-right font-mono text-slate-300">{p.bid.toFixed(2)}</td>
                          <td className="px-2 py-2 text-right font-mono text-slate-300">{p.ask.toFixed(2)}</td>
                          <td className="px-2 py-2 text-right font-mono text-slate-300">{(p.volume / 1000).toFixed(1)}K</td>
                          <td className="px-2 py-2 text-right font-mono text-slate-300">{(p.open_interest / 1000).toFixed(0)}K</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </ChartCard>
            </div>
          </div>
        )}

        {/* Strategy Builder Tab */}
        {activeTab === "strategy" && (
          <div className="space-y-4">
            <ChartCard title="Strategy Builder">
              <div className="space-y-4">
                <div>
                  <label className="text-xs text-slate-400 uppercase mb-2 block">Strategy</label>
                  <div className="flex flex-wrap gap-2">
                    {strategies.map(s => (
                      <button key={s.name} onClick={() => setSelectedStrategy(s.name)}
                        className={`px-3 py-2 rounded-lg text-xs font-medium transition-all ${selectedStrategy === s.name ? "bg-accent/15 text-accent border border-accent/30" : "bg-dark-700 text-slate-400 border border-dark-600 hover:text-white"}`}>
                        {s.name.replace(/_/g, " ")}
                      </button>
                    ))}
                  </div>
                  {strategies.find(s => s.name === selectedStrategy) && (
                    <p className="text-xs text-slate-400 mt-2">{strategies.find(s => s.name === selectedStrategy)?.description}</p>
                  )}
                </div>

                <div>
                  <div className="flex items-center justify-between mb-2">
                    <label className="text-xs text-slate-400 uppercase">Legs</label>
                    <button onClick={addLeg} className="text-xs text-accent hover:text-accent-hover">+ Add Leg</button>
                  </div>
                  <div className="space-y-2">
                    {strategyLegs.map((leg, i) => (
                      <div key={i} className="flex items-center gap-2 p-3 rounded-lg bg-dark-700 border border-dark-600">
                        <select value={leg.option_type} onChange={e => updateLeg(i, "option_type", e.target.value)}
                          className="px-2 py-1 rounded bg-dark-600 border border-dark-500 text-xs text-white">
                          <option value="call">Call</option>
                          <option value="put">Put</option>
                        </select>
                        <select value={leg.action} onChange={e => updateLeg(i, "action", e.target.value)}
                          className="px-2 py-1 rounded bg-dark-600 border border-dark-500 text-xs text-white">
                          <option value="buy">Buy</option>
                          <option value="sell">Sell</option>
                        </select>
                        <select value={leg.strike} onChange={e => updateLeg(i, "strike", Number(e.target.value))}
                          className="px-2 py-1 rounded bg-dark-600 border border-dark-500 text-xs text-white">
                          {chain?.strikes.map(s => <option key={s} value={s}>{s}</option>)}
                          {!chain && <option value={0}>Select strike</option>}
                        </select>
                        <input type="number" value={leg.premium} onChange={e => updateLeg(i, "premium", Number(e.target.value))}
                          placeholder="Premium" className="w-20 px-2 py-1 rounded bg-dark-600 border border-dark-500 text-xs text-white" />
                        <input type="number" value={leg.quantity} onChange={e => updateLeg(i, "quantity", Number(e.target.value))}
                          min={1} className="w-16 px-2 py-1 rounded bg-dark-600 border border-dark-500 text-xs text-white" />
                        {strategyLegs.length > 1 && (
                          <button onClick={() => removeLeg(i)} className="text-danger hover:text-red-400 text-xs">✕</button>
                        )}
                      </div>
                    ))}
                  </div>
                </div>

                <button onClick={calculateStrategy} disabled={calculating}
                  className="flex items-center gap-2 px-5 py-2 rounded-lg bg-accent text-white text-sm font-semibold hover:bg-accent-hover transition-colors disabled:opacity-50">
                  {calculating ? <Loader2 className="w-4 h-4 animate-spin" /> : <Calculator className="w-4 h-4" />}
                  Calculate P&L
                </button>
              </div>
            </ChartCard>

            {/* Strategy Result */}
            {strategyResult && (
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                <ChartCard title="Strategy Summary">
                  <div className="space-y-3">
                    <div className="flex justify-between"><span className="text-slate-400 text-sm">Strategy</span><span className="text-white font-semibold">{strategyResult.name.replace(/_/g, " ")}</span></div>
                    <div className="flex justify-between"><span className="text-slate-400 text-sm">Max Profit</span><span className="text-success font-semibold">{formatCurrency(strategyResult.max_profit)}</span></div>
                    <div className="flex justify-between"><span className="text-slate-400 text-sm">Max Loss</span><span className="text-danger font-semibold">{formatCurrency(strategyResult.max_loss)}</span></div>
                    <div className="flex justify-between"><span className="text-slate-400 text-sm">Margin Required</span><span className="text-white font-semibold">{formatCurrency(strategyResult.margin_required)}</span></div>
                    {strategyResult.risk_reward_ratio && (
                      <div className="flex justify-between"><span className="text-slate-400 text-sm">Risk:Reward</span><span className="text-accent font-semibold">1:{strategyResult.risk_reward_ratio}</span></div>
                    )}
                    {strategyResult.breakeven.length > 0 && (
                      <div className="flex justify-between"><span className="text-slate-400 text-sm">Breakeven</span><span className="text-warning font-semibold">{strategyResult.breakeven.map(b => `₹${b.toFixed(0)}`).join(", ")}</span></div>
                    )}
                  </div>
                </ChartCard>

                <ChartCard title="P&L at Expiry">
                  <div className="h-64">
                    <ResponsiveContainer width="100%" height="100%">
                      <AreaChart data={strategyResult.pnl_at_expiry}>
                        <defs>
                          <linearGradient id="pnlGrad" x1="0" y1="0" x2="0" y2="1">
                            <stop offset="5%" stopColor="#22c55e" stopOpacity={0.3} />
                            <stop offset="95%" stopColor="#ef4444" stopOpacity={0.3} />
                          </linearGradient>
                        </defs>
                        <CartesianGrid strokeDasharray="3 3" stroke="#222240" />
                        <XAxis dataKey="price" stroke="#64748b" fontSize={10} tickFormatter={v => `₹${v}`} />
                        <YAxis stroke="#64748b" fontSize={10} tickFormatter={v => `₹${v}`} />
                        <Tooltip contentStyle={{ background: "#1a1a2e", border: "1px solid #222240", borderRadius: "8px", color: "#e2e8f0" }} formatter={(v) => [`₹${Number(v ?? 0).toFixed(0)}`, "P&L"]} />
                        <ReferenceLine y={0} stroke="#475569" />
                        <Area type="monotone" dataKey="pnl" stroke="#3b82f6" fill="url(#pnlGrad)" strokeWidth={2} />
                      </AreaChart>
                    </ResponsiveContainer>
                  </div>
                </ChartCard>
              </div>
            )}
          </div>
        )}

        {/* P&L Calculator Tab */}
        {activeTab === "pnl" && (
          <ChartCard title="Quick P&L Calculator">
            <p className="text-sm text-slate-400 mb-4">Select a strategy above and add legs to calculate P&L. Use the Strategy Builder tab for detailed analysis.</p>
            <div className="flex flex-col items-center justify-center h-48 text-slate-500">
              <BarChart3 className="w-10 h-10 mb-3 opacity-50" />
              <p className="text-sm">Switch to Strategy Builder to create and analyze strategies</p>
            </div>
          </ChartCard>
        )}

        {loading && (
          <div className="flex items-center justify-center h-32">
            <Loader2 className="w-8 h-8 animate-spin text-accent" />
          </div>
        )}
      </div>
    </DashboardLayout>
  );
}
