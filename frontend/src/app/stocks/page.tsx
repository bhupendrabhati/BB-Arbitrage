"use client";

import { useEffect, useState, useRef } from "react";
import DashboardLayout from "@/components/DashboardLayout";
import Badge from "@/components/Badge";
import ChartCard from "@/components/ChartCard";
import SmartSuggestions, { generateStockSuggestions } from "@/components/SmartSuggestions";
import { api } from "@/lib/api";
import { TrendingUp, Search, RefreshCw, Loader2, ToggleLeft, ToggleRight, Plus, X, IndianRupee, DollarSign } from "lucide-react";

interface StockPrice {
  symbol: string;
  name: string;
  market: string;
  price: string;
  currency: string;
  volume: number;
  change_pct: string;
}

interface SpreadData {
  symbol: string;
  name: string;
  nse_price: string;
  bse_price: string;
  spread: string;
  spread_pct: string;
  buy_exchange: string;
  sell_exchange: string;
  profitable: boolean;
}

const INDIAN_STOCKS: Record<string, string> = {
  RELIANCE: "Reliance Industries", TCS: "Tata Consultancy", INFY: "Infosys",
  HDFCBANK: "HDFC Bank", SBIN: "SBI", ITC: "ITC", TATAMOTORS: "Tata Motors",
  WIPRO: "Wipro", ONGC: "ONGC", TATAPOWER: "Tata Power", HINDUNILVR: "Hindustan Unilever",
  BHARTIARTL: "Bharti Airtel", KOTAKBANK: "Kotak Bank", ICICIBANK: "ICICI Bank",
  LT: "Larsen & Toubro", AXISBANK: "Axis Bank", ASIANPAINT: "Asian Paints",
  MARUTI: "Maruti Suzuki", TITAN: "Titan", SUNPHARMA: "Sun Pharma",
  DRREDDY: "Dr Reddy's", CIPLA: "Cipla", TATACONSUM: "Tata Consumer",
  ULTRACEMCO: "UltraTech Cement", NESTLEIND: "Nestle India", GRASIM: "Grasim",
  HCLTECH: "HCL Technologies", TECHM: "Tech Mahindra", ADANIENT: "Adani Enterprises",
  JSWSTEEL: "JSW Steel", TATASTEEL: "Tata Steel", COALINDIA: "Coal India",
  NTPC: "NTPC", POWERGRID: "Power Grid", BPCL: "BPCL", HINDALCO: "Hindalco",
  VEDL: "Vedanta", YESBANK: "Yes Bank", BAJAJFINANCE: "Bajaj Finance",
  "BAJAJ-AUTO": "Bajaj Auto", HEROMOTOCO: "Hero Moto", EICHERMOT: "Eicher Motors",
};

const US_STOCKS: Record<string, string> = {
  AAPL: "Apple", MSFT: "Microsoft", GOOGL: "Alphabet", AMZN: "Amazon",
  TSLA: "Tesla", NVDA: "NVIDIA", AMD: "AMD", META: "Meta",
  SOFI: "SoFi Technologies", NIO: "NIO", JPM: "JPMorgan", V: "Visa",
  WMT: "Walmart", JNJ: "J&J", MA: "Mastercard", PG: "Procter & Gamble",
  UNH: "UnitedHealth", HD: "Home Depot", DIS: "Disney", NFLX: "Netflix",
  PYPL: "PayPal", BA: "Boeing", CRM: "Salesforce", INTC: "Intel",
};

const ALL_SUGGESTIONS = [
  ...Object.entries(INDIAN_STOCKS).map(([s, n]) => ({ symbol: s, name: n, market: "Indian" })),
  ...Object.entries(US_STOCKS).map(([s, n]) => ({ symbol: s, name: n, market: "US" })),
];

export default function StocksPage() {
  const [mode, setMode] = useState<"specific" | "auto">("specific");
  const [market, setMarket] = useState<"indian" | "us" | "both">("indian");
  const [exchange, setExchange] = useState<"bse" | "nse" | "both">("both");
  const [maxPrice, setMaxPrice] = useState(500);
  const [specificStocks, setSpecificStocks] = useState<string[]>(Object.keys(INDIAN_STOCKS).slice(0, 10));
  const [newStock, setNewStock] = useState("");
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [stockPrices, setStockPrices] = useState<StockPrice[]>([]);
  const [spreads, setSpreads] = useState<SpreadData[]>([]);
  const [autoResults, setAutoResults] = useState<StockPrice[]>([]);
  const [autoSpreads, setAutoSpreads] = useState<SpreadData[]>([]);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState<"prices" | "spreads">("prices");
  const inputRef = useRef<HTMLInputElement>(null);
  const wrapperRef = useRef<HTMLDivElement>(null);

  const suggestions = newStock.length >= 1
    ? ALL_SUGGESTIONS.filter(
        s => (s.symbol.toLowerCase().includes(newStock.toLowerCase()) || s.name.toLowerCase().includes(newStock.toLowerCase())) && !specificStocks.includes(s.symbol)
      ).slice(0, 8)
    : [];

  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (wrapperRef.current && !wrapperRef.current.contains(e.target as Node)) {
        setShowSuggestions(false);
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const fetchSpecificPrices = async () => {
    setLoading(true);
    const results: StockPrice[] = [];
    for (const symbol of specificStocks) {
      try {
        const marketHint = market === "us" ? "us" : market === "indian" ? "auto" : "auto";
        const data = await api.stockPrice(symbol, marketHint);
        if (data && data.symbol) {
          if (exchange === "both" || market === "us" || data.market?.toUpperCase() === exchange.toUpperCase()) {
            results.push(data);
          }
        }
      } catch {}
    }
    setStockPrices(results);
    setLoading(false);
  };

  const fetchSpecificSpreads = async () => {
    if (market === "us") return;
    setLoading(true);
    const results: SpreadData[] = [];
    for (const symbol of specificStocks) {
      try {
        const data = await api.stockSpread(symbol);
        if (data && data.symbol) results.push(data);
      } catch {}
    }
    setSpreads(results);
    setLoading(false);
  };

  const runAutoDiscover = async () => {
    setLoading(true);
    try {
      const prices = await api.scanStocks(maxPrice, market);
      setAutoResults((prices.stocks || []).filter((p: StockPrice) => p?.symbol));
      if (market !== "us") {
        const spreadsData = await api.autoDiscover(maxPrice);
        setAutoSpreads((spreadsData.opportunities || []).filter((s: SpreadData) => s?.symbol));
      }
    } catch {}
    setLoading(false);
  };

  useEffect(() => {
    if (mode === "specific") {
      fetchSpecificPrices();
      if (market !== "us" && exchange === "both") fetchSpecificSpreads();
    }
  }, [mode, specificStocks, market, exchange]);

  const addStock = (symbol?: string) => {
    const s = (symbol || newStock).toUpperCase().trim();
    if (s && !specificStocks.includes(s)) {
      setSpecificStocks([...specificStocks, s]);
      setNewStock("");
      setShowSuggestions(false);
    }
  };

  const removeStock = (symbol: string) => {
    setSpecificStocks(specificStocks.filter(s => s !== symbol));
  };

  const switchMarket = (m: "indian" | "us" | "both") => {
    setMarket(m);
    if (mode === "specific") {
      setSpecificStocks(m === "us" ? Object.keys(US_STOCKS) : m === "indian" ? Object.keys(INDIAN_STOCKS).slice(0, 10) : [...Object.keys(INDIAN_STOCKS).slice(0, 5), ...Object.keys(US_STOCKS).slice(0, 5)]);
    }
  };

  return (
    <DashboardLayout>
      <div className="space-y-6">
        <div>
          <h1 className="text-2xl font-bold text-white">Stocks</h1>
          <p className="text-sm text-slate-400 mt-1">BSE-NSE & US Stock Arbitrage Scanner</p>
        </div>

        <div className="flex items-center gap-4 p-4 rounded-xl border border-dark-600 bg-dark-800">
          <span className="text-sm text-slate-400">Discovery Mode:</span>
          <button onClick={() => setMode("specific")} className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all ${mode === "specific" ? "bg-accent/15 text-accent border border-accent/30" : "bg-dark-700 text-slate-400 border border-dark-600 hover:text-white"}`}>
            {mode === "specific" ? <ToggleRight className="w-4 h-4" /> : <ToggleLeft className="w-4 h-4" />}
            Specific Stocks
          </button>
          <button onClick={() => setMode("auto")} className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all ${mode === "auto" ? "bg-accent/15 text-accent border border-accent/30" : "bg-dark-700 text-slate-400 border border-dark-600 hover:text-white"}`}>
            {mode === "auto" ? <ToggleRight className="w-4 h-4" /> : <ToggleLeft className="w-4 h-4" />}
            Auto-Discover
          </button>
        </div>

        <div className="flex items-center gap-3">
          <span className="text-sm text-slate-400">Market:</span>
          {(["indian", "us", "both"] as const).map((m) => (
            <button key={m} onClick={() => switchMarket(m)} className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${market === m ? "bg-accent/15 text-accent border border-accent/30" : "bg-dark-700 text-slate-400 border border-dark-600 hover:text-white"}`}>
              {m === "indian" && <IndianRupee className="w-3 h-3" />}
              {m === "us" && <DollarSign className="w-3 h-3" />}
              {m === "both" && <><IndianRupee className="w-3 h-3" /><DollarSign className="w-3 h-3" /></>}
              {m.charAt(0).toUpperCase() + m.slice(1)}
            </button>
          ))}
          {market !== "us" && (
            <>
              <span className="text-slate-600 mx-1">|</span>
              <span className="text-sm text-slate-400">Exchange:</span>
              {(["nse", "bse", "both"] as const).map((e) => (
                <button key={e} onClick={() => setExchange(e)} className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${exchange === e ? "bg-accent/15 text-accent border border-accent/30" : "bg-dark-700 text-slate-400 border border-dark-600 hover:text-white"}`}>
                  {e.toUpperCase()}
                </button>
              ))}
            </>
          )}
        </div>

        {mode === "specific" && (
          <SmartSuggestions suggestions={generateStockSuggestions(stockPrices, spreads)} title="Stock Analysis" />
        )}

        {mode === "specific" && (
          <div className="space-y-4">
            <div className="flex items-center gap-2" ref={wrapperRef}>
              <div className="relative flex-1 max-w-xs">
                <input
                  ref={inputRef}
                  type="text"
                  value={newStock}
                  onChange={(e) => { setNewStock(e.target.value); setShowSuggestions(true); }}
                  onFocus={() => setShowSuggestions(true)}
                  onKeyDown={(e) => { if (e.key === "Enter") { e.preventDefault(); addStock(); } }}
                  placeholder="Search stock symbol or name..."
                  className="w-full pl-3 pr-10 py-2 rounded-lg bg-dark-700 border border-dark-600 text-sm text-white placeholder-slate-500 focus:outline-none focus:border-accent"
                />
                <button onClick={() => addStock()} className="absolute right-2 top-1/2 -translate-y-1/2 text-accent hover:text-accent-hover">
                  <Plus className="w-4 h-4" />
                </button>
                {showSuggestions && suggestions.length > 0 && (
                  <div className="absolute z-50 top-full mt-1 w-full bg-dark-700 border border-dark-600 rounded-lg shadow-xl max-h-60 overflow-y-auto">
                    {suggestions.map(s => (
                      <button
                        key={s.symbol}
                        onClick={() => addStock(s.symbol)}
                        className="w-full flex items-center justify-between px-3 py-2 text-sm hover:bg-dark-600 transition-colors text-left"
                      >
                        <div>
                          <span className="font-semibold text-white">{s.symbol}</span>
                          <span className="text-slate-400 ml-2 text-xs">{s.name}</span>
                        </div>
                        <Badge variant={s.market === "Indian" ? "success" : "purple"}>{s.market}</Badge>
                      </button>
                    ))}
                  </div>
                )}
              </div>
              <button
                onClick={() => { fetchSpecificPrices(); if (market !== "us") fetchSpecificSpreads(); }}
                disabled={loading}
                className="flex items-center gap-2 px-4 py-2 rounded-lg bg-accent/15 text-accent border border-accent/30 text-sm font-medium hover:bg-accent/25 transition-colors disabled:opacity-50"
              >
                {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <RefreshCw className="w-4 h-4" />}
                Refresh
              </button>
            </div>

            <div className="flex flex-wrap gap-2">
              {specificStocks.map((s, i) => (
                <span key={`${s}-${i}`} className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-dark-700 border border-dark-600 text-sm text-white">
                  {s}
                  <button onClick={() => removeStock(s)} className="text-slate-500 hover:text-danger"><X className="w-3 h-3" /></button>
                </span>
              ))}
            </div>

            <div className="flex gap-2">
              <button onClick={() => setActiveTab("prices")} className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${activeTab === "prices" ? "bg-accent/15 text-accent border border-accent/30" : "bg-dark-700 text-slate-400 border border-dark-600"}`}>
                Stock Prices
              </button>
              {market !== "us" && exchange === "both" && (
                <button onClick={() => setActiveTab("spreads")} className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${activeTab === "spreads" ? "bg-accent/15 text-accent border border-accent/30" : "bg-dark-700 text-slate-400 border border-dark-600"}`}>
                  BSE-NSE Spreads
                </button>
              )}
            </div>

            {activeTab === "prices" && (
              <div className="overflow-x-auto rounded-xl border border-dark-600">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b border-dark-600 bg-dark-700/50">
                      <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wider text-slate-400">Symbol</th>
                      <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wider text-slate-400">Name</th>
                      <th className="px-4 py-3 text-center text-xs font-semibold uppercase tracking-wider text-slate-400">Market</th>
                      <th className="px-4 py-3 text-right text-xs font-semibold uppercase tracking-wider text-slate-400">Price</th>
                      <th className="px-4 py-3 text-right text-xs font-semibold uppercase tracking-wider text-slate-400">Change</th>
                      <th className="px-4 py-3 text-right text-xs font-semibold uppercase tracking-wider text-slate-400">Volume</th>
                      <th className="px-4 py-3 text-right text-xs font-semibold uppercase tracking-wider text-slate-400">INR Value</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-dark-600">
                    {stockPrices.map((p, i) => (
                      <tr key={`price-${p.symbol || i}`} className="hover:bg-dark-700/30 transition-colors">
                        <td className="px-4 py-3 font-semibold text-white">{p.symbol}</td>
                        <td className="px-4 py-3 text-slate-300 text-xs">{p.name}</td>
                        <td className="px-4 py-3 text-center"><Badge variant={p.market === "NSE" ? "success" : p.market === "BSE" ? "info" : "purple"}>{p.market}</Badge></td>
                        <td className="px-4 py-3 text-right font-mono text-white">{p.currency === "INR" ? "₹" : "$"}{p.price}</td>
                        <td className="px-4 py-3 text-right font-mono">
                          <span className={Number(p.change_pct) >= 0 ? "text-success" : "text-danger"}>
                            {Number(p.change_pct) >= 0 ? "+" : ""}{p.change_pct}%
                          </span>
                        </td>
                        <td className="px-4 py-3 text-right text-slate-300 font-mono text-xs">{(p.volume || 0).toLocaleString()}</td>
                        <td className="px-4 py-3 text-right font-mono text-slate-300">
                          {p.currency === "INR" ? `₹${Number(p.price).toFixed(2)}` : `₹${(Number(p.price) * 85).toFixed(0)}`}
                        </td>
                      </tr>
                    ))}
                    {stockPrices.length === 0 && !loading && (
                      <tr><td colSpan={7} className="px-4 py-8 text-center text-slate-500 text-sm">No data yet. Click Refresh.</td></tr>
                    )}
                  </tbody>
                </table>
              </div>
            )}

            {activeTab === "spreads" && (
              <div className="overflow-x-auto rounded-xl border border-dark-600">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b border-dark-600 bg-dark-700/50">
                      <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wider text-slate-400">Symbol</th>
                      <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wider text-slate-400">Name</th>
                      <th className="px-4 py-3 text-right text-xs font-semibold uppercase tracking-wider text-slate-400">NSE Price</th>
                      <th className="px-4 py-3 text-right text-xs font-semibold uppercase tracking-wider text-slate-400">BSE Price</th>
                      <th className="px-4 py-3 text-right text-xs font-semibold uppercase tracking-wider text-slate-400">Spread</th>
                      <th className="px-4 py-3 text-center text-xs font-semibold uppercase tracking-wider text-slate-400">Action</th>
                      <th className="px-4 py-3 text-center text-xs font-semibold uppercase tracking-wider text-slate-400">Status</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-dark-600">
                    {spreads.map((s, i) => (
                      <tr key={`spread-${s.symbol || i}`} className="hover:bg-dark-700/30 transition-colors">
                        <td className="px-4 py-3 font-semibold text-white">{s.symbol}</td>
                        <td className="px-4 py-3 text-slate-300 text-xs">{s.name}</td>
                        <td className="px-4 py-3 text-right font-mono text-slate-300">₹{s.nse_price}</td>
                        <td className="px-4 py-3 text-right font-mono text-slate-300">₹{s.bse_price}</td>
                        <td className="px-4 py-3 text-right font-mono">
                          <span className={s.profitable ? "text-success" : "text-warning"}>₹{s.spread} ({s.spread_pct}%)</span>
                        </td>
                        <td className="px-4 py-3 text-center text-xs text-slate-300">
                          Buy {s.buy_exchange} → Sell {s.sell_exchange}
                        </td>
                        <td className="px-4 py-3 text-center">
                          <Badge variant={s.profitable ? "success" : "warning"}>
                            {s.profitable ? "PROFITABLE" : "SPREAD TOO LOW"}
                          </Badge>
                        </td>
                      </tr>
                    ))}
                    {spreads.length === 0 && !loading && (
                      <tr><td colSpan={7} className="px-4 py-8 text-center text-slate-500 text-sm">No spread data. Click Refresh.</td></tr>
                    )}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        )}

        {mode === "auto" && (
          <div className="space-y-4">
            <div className="flex items-center gap-4">
              <div className="flex items-center gap-2">
                <span className="text-sm text-slate-400">Max Price:</span>
                <input
                  type="number"
                  value={maxPrice}
                  onChange={(e) => setMaxPrice(Number(e.target.value))}
                  className="w-24 px-3 py-2 rounded-lg bg-dark-700 border border-dark-600 text-sm text-white focus:outline-none focus:border-accent"
                />
                <span className="text-xs text-slate-500">INR</span>
              </div>
              <button
                onClick={runAutoDiscover}
                disabled={loading}
                className="flex items-center gap-2 px-5 py-2 rounded-lg bg-accent text-white text-sm font-semibold hover:bg-accent-hover transition-colors disabled:opacity-50"
              >
                {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Search className="w-4 h-4" />}
                Scan Market
              </button>
            </div>

            {autoResults.length > 0 && (
              <ChartCard title={`Found ${autoResults.length} Affordable Stocks`}>
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="border-b border-dark-600">
                        <th className="px-3 py-2 text-left text-xs font-semibold uppercase text-slate-400">Symbol</th>
                        <th className="px-3 py-2 text-left text-xs font-semibold uppercase text-slate-400">Name</th>
                        <th className="px-3 py-2 text-center text-xs font-semibold uppercase text-slate-400">Market</th>
                        <th className="px-3 py-2 text-right text-xs font-semibold uppercase text-slate-400">Price</th>
                        <th className="px-3 py-2 text-right text-xs font-semibold uppercase text-slate-400">INR</th>
                        <th className="px-3 py-2 text-right text-xs font-semibold uppercase text-slate-400">Change</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-dark-600">
                      {autoResults.map((p, i) => (
                        <tr key={`auto-${p.symbol || i}`} className="hover:bg-dark-700/30">
                          <td className="px-3 py-2 font-semibold text-white">{p.symbol}</td>
                          <td className="px-3 py-2 text-slate-300 text-xs">{p.name}</td>
                          <td className="px-3 py-2 text-center"><Badge variant={p.market === "NSE" ? "success" : "purple"}>{p.market}</Badge></td>
                          <td className="px-3 py-2 text-right font-mono text-white">{p.currency === "INR" ? "₹" : "$"}{p.price}</td>
                          <td className="px-3 py-2 text-right font-mono text-slate-300">₹{p.currency === "INR" ? Number(p.price).toFixed(2) : (Number(p.price) * 85).toFixed(0)}</td>
                          <td className="px-3 py-2 text-right font-mono">
                            <span className={Number(p.change_pct) >= 0 ? "text-success" : "text-danger"}>
                              {Number(p.change_pct) >= 0 ? "+" : ""}{p.change_pct}%
                            </span>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </ChartCard>
            )}

            {autoSpreads.length > 0 && (
              <ChartCard title={`BSE-NSE Arbitrage: ${autoSpreads.length} Opportunities`}>
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="border-b border-dark-600">
                        <th className="px-3 py-2 text-left text-xs font-semibold uppercase text-slate-400">Symbol</th>
                        <th className="px-3 py-2 text-right text-xs font-semibold uppercase text-slate-400">NSE</th>
                        <th className="px-3 py-2 text-right text-xs font-semibold uppercase text-slate-400">BSE</th>
                        <th className="px-3 py-2 text-right text-xs font-semibold uppercase text-slate-400">Spread</th>
                        <th className="px-3 py-2 text-center text-xs font-semibold uppercase text-slate-400">Action</th>
                        <th className="px-3 py-2 text-center text-xs font-semibold uppercase text-slate-400">Status</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-dark-600">
                      {autoSpreads.map((s, i) => (
                        <tr key={`autospread-${s.symbol || i}`} className="hover:bg-dark-700/30">
                          <td className="px-3 py-2 font-semibold text-white">{s.symbol}</td>
                          <td className="px-3 py-2 text-right font-mono text-slate-300">₹{s.nse_price}</td>
                          <td className="px-3 py-2 text-right font-mono text-slate-300">₹{s.bse_price}</td>
                          <td className="px-3 py-2 text-right font-mono">
                            <span className={s.profitable ? "text-success" : "text-warning"}>₹{s.spread} ({s.spread_pct}%)</span>
                          </td>
                          <td className="px-3 py-2 text-center text-xs text-slate-300">Buy {s.buy_exchange} → Sell {s.sell_exchange}</td>
                          <td className="px-3 py-2 text-center">
                            <Badge variant={s.profitable ? "success" : "warning"}>
                              {s.profitable ? "PROFITABLE" : "LOW"}
                            </Badge>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </ChartCard>
            )}

            {!loading && autoResults.length === 0 && (
              <div className="flex flex-col items-center justify-center h-48 text-slate-500">
                <Search className="w-10 h-10 mb-3 opacity-50" />
                <p className="text-sm">Click &quot;Scan Market&quot; to discover affordable stocks</p>
              </div>
            )}
          </div>
        )}
      </div>
    </DashboardLayout>
  );
}
