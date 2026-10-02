import asyncio
from decimal import Decimal
from dataclasses import dataclass, field
from typing import Optional
import math
import random
from datetime import datetime, timezone, timedelta

import yfinance as yf


@dataclass
class OptionContract:
    symbol: str
    expiry: str
    strike: float
    option_type: str  # "call" or "put"
    last_price: float
    bid: float
    ask: float
    volume: int
    open_interest: int
    implied_volatility: float
    delta: float
    gamma: float
    theta: float
    vega: float
    in_the_money: bool


@dataclass
class OptionChain:
    symbol: str
    current_price: float
    expiry_dates: list[str]
    selected_expiry: str
    calls: list[OptionContract]
    puts: list[OptionContract]
    strikes: list[float]


@dataclass
class StrategyLeg:
    option_type: str
    action: str  # "buy" or "sell"
    strike: float
    expiry: str
    quantity: int
    premium: float


@dataclass
class StrategyResult:
    name: str
    description: str
    legs: list[StrategyLeg]
    max_profit: Optional[float]
    max_loss: Optional[float]
    breakeven: list[float]
    margin_required: float
    risk_reward_ratio: Optional[float]
    pnl_at_expiry: list[dict]


def _black_scholes_greeks(S: float, K: float, T: float, r: float, sigma: float, option_type: str) -> dict:
    if T <= 0 or sigma <= 0:
        return {"delta": 0, "gamma": 0, "theta": 0, "vega": 0, "price": 0}

    d1 = (math.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * math.sqrt(T))
    d2 = d1 - sigma * math.sqrt(T)

    from scipy.stats import norm
    N_d1 = norm.cdf(d1)
    N_d2 = norm.cdf(d2)
    n_d1 = norm.pdf(d1)

    if option_type == "call":
        price = S * N_d2 - K * math.exp(-r * T) * norm.cdf(-d2)
        delta = N_d1 - 1
    else:
        price = K * math.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1)
        delta = N_d1 - 1

    gamma = n_d1 / (S * sigma * math.sqrt(T))
    theta = (-(S * n_d1 * sigma) / (2 * math.sqrt(T)) - r * K * math.exp(-r * T) * norm.cdf(-d2)) / 365
    vega = S * n_d1 * math.sqrt(T) / 100

    if option_type == "put":
        delta += 1

    return {
        "delta": round(float(delta), 4),
        "gamma": round(float(gamma), 6),
        "theta": round(float(theta), 4),
        "vega": round(float(vega), 4),
        "price": round(float(price), 2),
    }


class OptionsService:
    def __init__(self):
        self._cache: dict[str, dict] = {}

    async def get_option_chain(self, symbol: str, expiry: Optional[str] = None) -> Optional[OptionChain]:
        try:
            ticker = yf.Ticker(symbol)
            current_price = ticker.fast_info.get("lastPrice", ticker.fast_info.get("previousClose", 0))
            if not current_price:
                info = ticker.info
                current_price = info.get("currentPrice", info.get("regularMarketPrice", 0))

            expirations = list(ticker.options or [])
            if not expirations:
                return None

            selected_expiry = expiry if expiry and expiry in expirations else expirations[0]
            chain = ticker.option_chain(selected_expiry)

            calls = []
            for _, row in chain.calls.iterrows():
                try:
                    strike = float(row["strike"])
                    iv = float(row.get("impliedVolatility", 0) or 0)
                    T = max((datetime.strptime(selected_expiry, "%Y-%m-%d").date() - datetime.now(timezone.utc).date()).days, 1) / 365.0
                    greeks = _black_scholes_greeks(current_price, strike, T, 0.05, max(iv, 0.01), "call")

                    calls.append(OptionContract(
                        symbol=symbol, expiry=selected_expiry, strike=strike,
                        option_type="call",
                        last_price=float(row.get("lastPrice", 0) or 0),
                        bid=float(row.get("bid", 0) or 0),
                        ask=float(row.get("ask", 0) or 0),
                        volume=int(row.get("volume", 0) or 0),
                        open_interest=int(row.get("openInterest", 0) or 0),
                        implied_volatility=iv,
                        delta=greeks["delta"], gamma=greeks["gamma"],
                        theta=greeks["theta"], vega=greeks["vega"],
                        in_the_money=bool(row.get("inTheMoney", False)),
                    ))
                except Exception:
                    continue

            puts = []
            for _, row in chain.puts.iterrows():
                try:
                    strike = float(row["strike"])
                    iv = float(row.get("impliedVolatility", 0) or 0)
                    T = max((datetime.strptime(selected_expiry, "%Y-%m-%d").date() - datetime.now(timezone.utc).date()).days, 1) / 365.0
                    greeks = _black_scholes_greeks(current_price, strike, T, 0.05, max(iv, 0.01), "put")

                    puts.append(OptionContract(
                        symbol=symbol, expiry=selected_expiry, strike=strike,
                        option_type="put",
                        last_price=float(row.get("lastPrice", 0) or 0),
                        bid=float(row.get("bid", 0) or 0),
                        ask=float(row.get("ask", 0) or 0),
                        volume=int(row.get("volume", 0) or 0),
                        open_interest=int(row.get("openInterest", 0) or 0),
                        implied_volatility=iv,
                        delta=greeks["delta"], gamma=greeks["gamma"],
                        theta=greeks["theta"], vega=greeks["vega"],
                        in_the_money=bool(row.get("inTheMoney", False)),
                    ))
                except Exception:
                    continue

            strikes = sorted(set(c.strike for c in calls))

            return OptionChain(
                symbol=symbol, current_price=float(current_price),
                expiry_dates=expirations, selected_expiry=selected_expiry,
                calls=calls, puts=puts, strikes=strikes,
            )
        except Exception:
            return None

    async def get_indian_fno(self, symbol: str) -> Optional[OptionChain]:
        indian_symbols = {
            "NIFTY": {"spot": 24500, "strike_step": 50, "expiry_base": "2026-09-25"},
            "BANKNIFTY": {"spot": 51200, "strike_step": 100, "expiry_base": "2026-09-25"},
            "RELIANCE": {"spot": 1250, "strike_step": 20, "expiry_base": "2026-09-25"},
            "TCS": {"spot": 2090, "strike_step": 20, "expiry_base": "2026-09-25"},
            "INFY": {"spot": 1020, "strike_step": 10, "expiry_base": "2026-09-25"},
            "SBIN": {"spot": 994, "strike_step": 10, "expiry_base": "2026-09-25"},
            "HDFCBANK": {"spot": 1700, "strike_step": 20, "expiry_base": "2026-09-25"},
            "TATAMOTORS": {"spot": 680, "strike_step": 10, "expiry_base": "2026-09-25"},
            "ITC": {"spot": 460, "strike_step": 5, "expiry_base": "2026-09-25"},
            "WIPRO": {"spot": 280, "strike_step": 5, "expiry_base": "2026-09-25"},
        }

        if symbol not in indian_symbols:
            return None

        config = indian_symbols[symbol]
        spot = config["spot"]
        step = config["strike_step"]
        base_date = datetime.strptime(config["expiry_base"], "%Y-%m-%d").date()

        expiry_dates = [
            (base_date + timedelta(days=d)).strftime("%Y-%m-%d")
            for d in [0, 7, 14, 30]
        ]
        selected_expiry = expiry_dates[0]

        strikes = [spot + i * step for i in range(-10, 11)]
        T = 7 / 365.0

        calls = []
        puts = []
        for K in strikes:
            iv_call = random.uniform(0.15, 0.45)
            iv_put = random.uniform(0.15, 0.45)

            call_greeks = _black_scholes_greeks(spot, K, T, 0.065, iv_call, "call")
            put_greeks = _black_scholes_greeks(spot, K, T, 0.065, iv_put, "put")

            moneyness = (spot - K) / spot
            base_oi = max(int(50000 * math.exp(-50 * moneyness ** 2)), 100)
            base_vol = max(int(base_oi * random.uniform(0.01, 0.1)), 10)

            calls.append(OptionContract(
                symbol=symbol, expiry=selected_expiry, strike=K,
                option_type="call",
                last_price=call_greeks["price"],
                bid=call_greeks["price"] * 0.98,
                ask=call_greeks["price"] * 1.02,
                volume=base_vol,
                open_interest=base_oi,
                implied_volatility=iv_call,
                delta=call_greeks["delta"], gamma=call_greeks["gamma"],
                theta=call_greeks["theta"], vega=call_greeks["vega"],
                in_the_money=spot > K,
            ))

            puts.append(OptionContract(
                symbol=symbol, expiry=selected_expiry, strike=K,
                option_type="put",
                last_price=put_greeks["price"],
                bid=put_greeks["price"] * 0.98,
                ask=put_greeks["price"] * 1.02,
                volume=base_vol,
                open_interest=base_oi,
                implied_volatility=iv_put,
                delta=put_greeks["delta"], gamma=put_greeks["gamma"],
                theta=put_greeks["theta"], vega=put_greeks["vega"],
                in_the_money=spot < K,
            ))

        return OptionChain(
            symbol=symbol, current_price=spot,
            expiry_dates=expiry_dates, selected_expiry=selected_expiry,
            calls=calls, puts=puts, strikes=strikes,
        )

    def calculate_strategy(self, name: str, legs: list[StrategyLeg], spot: float) -> StrategyResult:
        strategies = {
            "long_call": {"desc": "Bullish — profit if price rises", "max_profit": "unlimited", "max_loss": "premium_paid"},
            "long_put": {"desc": "Bearish — profit if price falls", "max_profit": "strike - premium", "max_loss": "premium_paid"},
            "covered_call": {"desc": "Neutral to mildly bullish", "max_profit": "premium + (strike - spot)", "max_loss": "spot - premium"},
            "straddle": {"desc": "Profit from large move in either direction", "max_profit": "unlimited", "max_loss": "total_premium"},
            "strangle": {"desc": "Cheaper straddle — needs bigger move", "max_profit": "unlimited", "max_loss": "total_premium"},
            "bull_call_spread": {"desc": "Limited profit/loss bullish", "max_profit": "spread - net_premium", "max_loss": "net_premium"},
            "bear_put_spread": {"desc": "Limited profit/loss bearish", "max_profit": "spread - net_premium", "max_loss": "net_premium"},
            "iron_condor": {"desc": "Profit from low volatility", "max_profit": "net_premium", "max_loss": "spread - net_premium"},
            "butterfly": {"desc": "Profit at specific price", "max_profit": "wing_width - net_premium", "max_loss": "net_premium"},
        }

        info = strategies.get(name, {"desc": name, "max_profit": "varies", "max_loss": "varies"})

        total_premium = sum(
            l.premium * l.quantity * (1 if l.action == "buy" else -1)
            for l in legs
        )

        pnl_points = []
        for pt in range(int(spot * 0.7), int(spot * 1.3), max(int(spot * 0.01), 1)):
            pnl = 0
            for leg in legs:
                if leg.option_type == "call":
                    intrinsic = max(pt - leg.strike, 0)
                else:
                    intrinsic = max(leg.strike - pt, 0)

                if leg.action == "buy":
                    pnl += (intrinsic - leg.premium) * leg.quantity * 100
                else:
                    pnl += (leg.premium - intrinsic) * leg.quantity * 100

            pnl_points.append({"price": pt, "pnl": round(pnl, 2)})

        max_profit = max(p["pnl"] for p in pnl_points) if pnl_points else 0
        max_loss = min(p["pnl"] for p in pnl_points) if pnl_points else 0

        breakeven = []
        for i in range(1, len(pnl_points)):
            if pnl_points[i - 1]["pnl"] < 0 and pnl_points[i]["pnl"] >= 0:
                breakeven.append(pnl_points[i]["price"])
            elif pnl_points[i - 1]["pnl"] >= 0 and pnl_points[i]["pnl"] < 0:
                breakeven.append(pnl_points[i]["price"])

        margin = sum(
            l.strike * l.quantity * 100 * 0.2
            for l in legs if l.action == "sell"
        )

        return StrategyResult(
            name=name, description=info["desc"],
            legs=legs, max_profit=max_profit, max_loss=max_loss,
            breakeven=breakeven, margin_required=margin,
            risk_reward_ratio=round(abs(max_profit / max_loss), 2) if max_loss != 0 else None,
            pnl_at_expiry=pnl_points,
        )


options_service = OptionsService()
