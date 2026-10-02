"use client";

import { TrendingUp, TrendingDown, AlertTriangle, Lightbulb, Target, Shield } from "lucide-react";

interface Suggestion {
  type: "buy" | "sell" | "hold" | "caution" | "tip";
  title: string;
  detail: string;
  confidence?: "high" | "medium" | "low";
}

const typeConfig = {
  buy: { icon: TrendingUp, color: "text-success", bg: "bg-success/10", border: "border-success/30" },
  sell: { icon: TrendingDown, color: "text-danger", bg: "bg-danger/10", border: "border-danger/30" },
  hold: { icon: Shield, color: "text-warning", bg: "bg-warning/10", border: "border-warning/30" },
  caution: { icon: AlertTriangle, color: "text-danger", bg: "bg-danger/10", border: "border-danger/30" },
  tip: { icon: Lightbulb, color: "text-accent", bg: "bg-accent/10", border: "border-accent/30" },
};

const confidenceBadge = {
  high: "bg-success/20 text-success",
  medium: "bg-warning/20 text-warning",
  low: "bg-slate-500/20 text-slate-400",
};

export default function SmartSuggestions({ suggestions, title = "Smart Suggestions" }: { suggestions: Suggestion[]; title?: string }) {
  if (!suggestions.length) return null;

  return (
    <div className="rounded-xl border border-dark-600 bg-dark-800 p-4">
      <div className="flex items-center gap-2 mb-3">
        <Lightbulb className="w-4 h-4 text-warning" />
        <h3 className="text-sm font-semibold text-white">{title}</h3>
      </div>
      <div className="space-y-2">
        {suggestions.map((s, i) => {
          const config = typeConfig[s.type];
          const Icon = config.icon;
          return (
            <div key={i} className={`flex items-start gap-3 p-3 rounded-lg ${config.bg} border ${config.border}`}>
              <Icon className={`w-4 h-4 mt-0.5 flex-shrink-0 ${config.color}`} />
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2">
                  <span className="text-sm font-semibold text-white">{s.title}</span>
                  {s.confidence && (
                    <span className={`text-[10px] px-1.5 py-0.5 rounded ${confidenceBadge[s.confidence]}`}>
                      {s.confidence}
                    </span>
                  )}
                </div>
                <p className="text-xs text-slate-400 mt-0.5">{s.detail}</p>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

export function generateCryptoSuggestions(opps: { symbol: string; buy_exchange: string; sell_exchange: string; gross_spread_percent: string; net_profit: string; status: string }[]): Suggestion[] {
  const suggestions: Suggestion[] = [];
  const executable = opps.filter(o => o.status === "executable");
  const bestSpread = opps.reduce((best, o) => Number(o.gross_spread_percent) > Number(best.gross_spread_percent) ? o : best, opps[0]);

  if (executable.length > 0) {
    suggestions.push({
      type: "buy", title: `${executable.length} Arbitrage Found`,
      detail: `Buy on ${executable[0].buy_exchange}, sell on ${executable[0].sell_exchange} for ${executable[0].symbol}. Net profit: $${executable[0].net_profit}`,
      confidence: "high",
    });
  }

  if (bestSpread && Number(bestSpread.gross_spread_percent) > 0.1) {
    suggestions.push({
      type: "tip", title: "Best Spread",
      detail: `${bestSpread.symbol}: ${bestSpread.gross_spread_percent}% spread between ${bestSpread.buy_exchange} and ${bestSpread.sell_exchange}`,
      confidence: "medium",
    });
  }

  const pairs = [...new Set(opps.map(o => o.symbol))];
  pairs.forEach(pair => {
    const pairOpps = opps.filter(o => o.symbol === pair);
    const pairExe = pairOpps.filter(o => o.status === "executable");
    if (pairExe.length === 0) {
      suggestions.push({
        type: "caution", title: `${pair} — No Opportunity`,
        detail: `Spread too small across all exchanges. Wait for volatility.`,
        confidence: "low",
      });
    }
  });

  suggestions.push({
    type: "tip", title: "How Crypto Arbitrage Works",
    detail: "Buy BTC/ETH on the cheaper exchange (Binance) and immediately sell on the more expensive one (Coinbase). Profit = price difference minus fees.",
  });

  suggestions.push({
    type: "caution", title: "Risk Warning",
    detail: "Arbitrage windows close in seconds. Use limit orders, account for withdrawal fees, and never invest more than you can afford to lose.",
  });

  return suggestions;
}

export function generateStockSuggestions(prices: { symbol: string; market: string; price: string; change_pct: string; volume: number }[], spreads: { symbol: string; spread_pct: string; profitable: boolean; buy_exchange: string; sell_exchange: string }[]): Suggestion[] {
  const suggestions: Suggestion[] = [];

  const gainers = prices.filter(p => Number(p.change_pct) > 0.5).sort((a, b) => Number(b.change_pct) - Number(a.change_pct));
  const losers = prices.filter(p => Number(p.change_pct) < -0.5).sort((a, b) => Number(a.change_pct) - Number(b.change_pct));

  if (gainers.length > 0) {
    suggestions.push({
      type: "buy", title: `Top Gainer: ${gainers[0].symbol}`,
      detail: `Up ${gainers[0].change_pct}% today at ₹${gainers[0].price}. Consider momentum buying with stop-loss.`,
      confidence: "medium",
    });
  }

  if (losers.length > 0) {
    suggestions.push({
      type: "sell", title: `Top Loser: ${losers[0].symbol}`,
      detail: `Down ${losers[0].change_pct}% today at ₹${losers[0].price}. May be a buying opportunity if fundamentals are strong.`,
      confidence: "medium",
    });
  }

  const profitableSpreads = spreads.filter(s => s.profitable);
  if (profitableSpreads.length > 0) {
    suggestions.push({
      type: "buy", title: `BSE-NSE Arbitrage: ${profitableSpreads[0].symbol}`,
      detail: `Buy on ${profitableSpreads[0].buy_exchange}, sell on ${profitableSpreads[0].sell_exchange}. Spread: ${profitableSpreads[0].spread_pct}%`,
      confidence: "high",
    });
  }

  suggestions.push({
    type: "tip", title: "Stock Investment Tips",
    detail: "For intraday: Look for stocks with >1% daily move and high volume. For swing: Check support/resistance levels. For BSE-NSE arb: Spread must be >0.5% to cover brokerage.",
  });

  suggestions.push({
    type: "tip", title: "Indian Market Timing",
    detail: "Markets open 9:15 AM - 3:30 PM IST. Best liquidity 9:30 AM - 2:30 PM. Avoid first and last 15 minutes.",
  });

  return suggestions;
}

export function generateFnOSuggestions(chain: { current_price: number; calls: { strike: number; delta: number; implied_volatility: number; volume: number }[]; puts: { strike: number; delta: number; implied_volatility: number; volume: number }[] } | null, strategy: string): Suggestion[] {
  const suggestions: Suggestion[] = [];
  if (!chain) return suggestions;

  const spot = chain.current_price;
  const atmStrike = chain.calls.reduce((closest, c) => Math.abs(c.strike - spot) < Math.abs(closest.strike - spot) ? c : closest).strike;
  const atmCall = chain.calls.find(c => c.strike === atmStrike);
  const atmPut = chain.puts.find(p => p.strike === atmStrike);

  if (atmCall) {
    const avgIV = chain.calls.reduce((sum, c) => sum + c.implied_volatility, 0) / chain.calls.length;
    if (atmCall.implied_volatility > avgIV * 1.3) {
      suggestions.push({
        type: "caution", title: "High IV — Selling May Be Better",
        detail: `ATM IV is ${(atmCall.implied_volatility * 100).toFixed(1)}% (above average). Consider selling options (strangle, iron condor) to collect premium.`,
        confidence: "high",
      });
    } else {
      suggestions.push({
        type: "buy", title: "Moderate IV — Buying May Work",
        detail: `ATM IV is ${(atmCall.implied_volatility * 100).toFixed(1)}%. Consider buying calls/puts if you expect a directional move.`,
        confidence: "medium",
      });
    }
  }

  const highOI = [...chain.calls, ...chain.puts].sort((a, b) => b.volume - a.volume).slice(0, 3);
  if (highOI.length > 0) {
    suggestions.push({
      type: "tip", title: "Most Active Contracts",
      detail: `Strike ${highOI[0].strike} has highest volume. This is the market's focus point. Trade near this strike for best liquidity.`,
      confidence: "medium",
    });
  }

  const bullishStrategies = ["long_call", "bull_call_spread"];
  const bearishStrategies = ["long_put", "bear_put_spread"];
  const neutralStrategies = ["straddle", "strangle", "iron_condor"];

  if (bullishStrategies.includes(strategy)) {
    suggestions.push({
      type: "buy", title: "Bullish Strategy Active",
      detail: "You're betting the price goes UP. Set a stop-loss if price drops below your breakeven. Consider closing at 50% profit.",
      confidence: "high",
    });
  } else if (bearishStrategies.includes(strategy)) {
    suggestions.push({
      type: "sell", title: "Bearish Strategy Active",
      detail: "You're betting the price goes DOWN. Set a stop-loss if price rises above your breakeven. Consider closing at 50% profit.",
      confidence: "high",
    });
  } else if (neutralStrategies.includes(strategy)) {
    suggestions.push({
      type: "tip", title: "Neutral Strategy Active",
      detail: "You profit from low volatility. Close before expiry if the price moves too far from your strikes. Time decay works in your favor.",
      confidence: "high",
    });
  }

  suggestions.push({
    type: "tip", title: "F&O Quick Guide",
    detail: "Call = right to buy (bullish). Put = right to sell (bearish). Buy options = limited risk, needs big move. Sell options = high risk, profits from time decay.",
  });

  suggestions.push({
    type: "caution", title: "Risk Warning",
    detail: "Options can expire worthless. Never invest more than 2-5% of capital on a single trade. Always use stop-losses.",
  });

  return suggestions;
}
