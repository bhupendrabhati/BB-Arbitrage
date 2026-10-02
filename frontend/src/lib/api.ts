const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

async function fetchAPI<T>(endpoint: string): Promise<T> {
  const res = await fetch(`${API_BASE}${endpoint}`, { cache: "no-store" });
  if (!res.ok) throw new Error(`API error: ${res.status}`);
  const json = await res.json();
  return json.data ?? json;
}

async function postAPI<T>(endpoint: string, body?: unknown): Promise<T> {
  const res = await fetch(`${API_BASE}${endpoint}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: body ? JSON.stringify(body) : undefined,
  });
  if (!res.ok) throw new Error(`API error: ${res.status}`);
  const json = await res.json();
  return json.data ?? json;
}

async function deleteAPI<T>(endpoint: string): Promise<T> {
  const res = await fetch(`${API_BASE}${endpoint}`, { method: "DELETE" });
  if (!res.ok) throw new Error(`API error: ${res.status}`);
  const json = await res.json();
  return json.data ?? json;
}

export const api = {
  health: () => fetchAPI<{ status: string; version: string; mode: string; live_trading_enabled: boolean; kill_switch_active: boolean }>("/api/health/"),
  root: () => fetchAPI<{ name: string; version: string; mode: string; live_trading_enabled: boolean }>("/"),
  tradingStatus: () => fetchAPI<{ mode: string; active: boolean }>("/api/trading/status"),
  trades: () => fetchAPI<{ trades: unknown[]; total: number }>("/api/trading/trades"),
  portfolio: () => fetchAPI<{ initial_capital: string; current_capital: string; total_pnl: string; total_trades: number; winning_trades: number; losing_trades: number; win_rate: string; max_drawdown: string }>("/api/portfolio/"),
  portfolioTrades: () => fetchAPI<{ trades: unknown[]; total: number }>("/api/portfolio/trades"),
  riskStatus: () => fetchAPI<{ daily_pnl: string; daily_trades: number; open_trades: number; total_exposure: string; daily_loss_limit: string; max_open_trades: number; max_trades_per_day: number; kill_switch_active: boolean }>("/api/risk/status"),
  killSwitch: () => fetchAPI<{ active: boolean; activated_at: string | null; reason: string }>("/api/risk/kill-switch"),
  activateKillSwitch: (reason: string) => postAPI<{ active: boolean; reason: string }>("/api/risk/kill-switch", { reason }),
  deactivateKillSwitch: () => deleteAPI<{ active: boolean }>("/api/risk/kill-switch"),
  opportunities: () => fetchAPI<{ opportunities: unknown[]; total: number }>("/api/opportunities/"),
  opportunityStats: () => fetchAPI<{ total: number; executable: number; rejected: number }>("/api/opportunities/stats/summary"),
  marketDataStatus: () => fetchAPI<{ status: string; exchanges: string[]; symbols: string[] }>("/api/market-data/status"),
  // Demo mode
  startDemo: () => postAPI<{ status: string; message: string }>("/api/demo/start"),
  demoOpportunities: () => fetchAPI<{ opportunities: unknown[]; total: number }>("/api/demo/opportunities"),
  demoPortfolio: () => fetchAPI<{ paper_trading: Record<string, string>; portfolio: Record<string, string>; risk: Record<string, string> }>("/api/demo/portfolio"),
  // Stocks
  stockPrice: (symbol: string, market?: string) => fetchAPI<{ symbol: string; name: string; market: string; price: string; currency: string; volume: number; change_pct: string }>(`/api/stocks/price/${symbol}?market=${market || "auto"}`),
  stockSpread: (symbol: string) => fetchAPI<{ symbol: string; name: string; nse_price: string; bse_price: string; spread: string; spread_pct: string; buy_exchange: string; sell_exchange: string; profitable: boolean }>(`/api/stocks/spread/${symbol}`),
  scanStocks: (maxPrice: number, market: string) => postAPI<{ stocks: { symbol: string; name: string; market: string; price: string; currency: string; volume: number; change_pct: string }[]; total: number }>("/api/stocks/scan", { max_price_inr: maxPrice, market }),
  autoDiscover: (maxPrice: number) => fetchAPI<{ opportunities: { symbol: string; name: string; nse_price: string; bse_price: string; spread: string; spread_pct: string; buy_exchange: string; sell_exchange: string; profitable: boolean }[]; total: number }>(`/api/stocks/auto-discover?max_price=${maxPrice}`),
  watchedStocks: () => fetchAPI<{ indian: Record<string, { name: string; sector: string; bse: string; nse: string }>; us: Record<string, { name: string; sector: string }>; affordable: string[] }>("/api/stocks/watched"),
  // F&O Options
  optionChain: (symbol: string, market: string, expiry?: string) => fetchAPI<{ symbol: string; current_price: number; expiry_dates: string[]; selected_expiry: string; strikes: number[]; calls: { strike: number; last_price: number; bid: number; ask: number; volume: number; open_interest: number; implied_volatility: number; delta: number; gamma: number; theta: number; vega: number; in_the_money: boolean }[]; puts: { strike: number; last_price: number; bid: number; ask: number; volume: number; open_interest: number; implied_volatility: number; delta: number; gamma: number; theta: number; vega: number; in_the_money: boolean }[] }>(`/api/options/chain/${symbol}?market=${market}${expiry ? `&expiry=${expiry}` : ""}`),
  optionStrategies: () => fetchAPI<{ name: string; description: string; legs: number; risk: string; reward: string }[]>("/api/options/strategies"),
  calculateStrategy: (data: { name: string; symbol: string; spot: number; legs: { option_type: string; action: string; strike: number; expiry: string; quantity: number; premium: number }[] }) => postAPI<{ name: string; description: string; max_profit: number; max_loss: number; breakeven: number[]; margin_required: number; risk_reward_ratio: number | null; pnl_at_expiry: { price: number; pnl: number }[]; legs: { option_type: string; action: string; strike: number; expiry: string; quantity: number; premium: number }[] }>("/api/options/strategy/calculate", data),
  indianFno: () => fetchAPI<{ symbols: { symbol: string; name: string; spot: number; type: string }[] }>("/api/options/indian"),
};
