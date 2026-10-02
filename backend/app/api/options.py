from fastapi import APIRouter, Query
from pydantic import BaseModel
from typing import Optional
from app.schemas.common import ResponseBase
from app.options.service import options_service, StrategyLeg

router = APIRouter()


class StrategyRequest(BaseModel):
    name: str
    symbol: str
    spot: float
    legs: list[dict]


@router.get("/chain/{symbol}")
async def get_option_chain(symbol: str, expiry: Optional[str] = None, market: str = "us"):
    if market == "indian":
        chain = await options_service.get_indian_fno(symbol.upper())
    else:
        chain = await options_service.get_option_chain(symbol.upper(), expiry)

    if not chain:
        return ResponseBase(success=False, error=f"No options data for {symbol}")

    return ResponseBase(data={
        "symbol": chain.symbol,
        "current_price": chain.current_price,
        "expiry_dates": chain.expiry_dates,
        "selected_expiry": chain.selected_expiry,
        "strikes": chain.strikes,
        "calls": [
            {
                "strike": c.strike, "last_price": c.last_price,
                "bid": round(c.bid, 2), "ask": round(c.ask, 2),
                "volume": c.volume, "open_interest": c.open_interest,
                "implied_volatility": round(c.implied_volatility, 4),
                "delta": c.delta, "gamma": c.gamma,
                "theta": c.theta, "vega": c.vega,
                "in_the_money": c.in_the_money,
            }
            for c in chain.calls
        ],
        "puts": [
            {
                "strike": p.strike, "last_price": p.last_price,
                "bid": round(p.bid, 2), "ask": round(p.ask, 2),
                "volume": p.volume, "open_interest": p.open_interest,
                "implied_volatility": round(p.implied_volatility, 4),
                "delta": p.delta, "gamma": p.gamma,
                "theta": p.theta, "vega": p.vega,
                "in_the_money": p.in_the_money,
            }
            for p in chain.puts
        ],
    })


@router.get("/strategies")
async def list_strategies():
    return ResponseBase(data=[
        {"name": "long_call", "description": "Bullish — profit if price rises", "legs": 1, "risk": "limited", "reward": "unlimited"},
        {"name": "long_put", "description": "Bearish — profit if price falls", "legs": 1, "risk": "limited", "reward": "unlimited"},
        {"name": "straddle", "description": "Profit from large move either direction", "legs": 2, "risk": "limited", "reward": "unlimited"},
        {"name": "strangle", "description": "Cheaper straddle — needs bigger move", "legs": 2, "risk": "limited", "reward": "unlimited"},
        {"name": "bull_call_spread", "description": "Limited profit/loss bullish play", "legs": 2, "risk": "limited", "reward": "limited"},
        {"name": "bear_put_spread", "description": "Limited profit/loss bearish play", "legs": 2, "risk": "limited", "reward": "limited"},
        {"name": "iron_condor", "description": "Profit from low volatility / sideways", "legs": 4, "risk": "limited", "reward": "limited"},
        {"name": "butterfly", "description": "Profit at a specific price point", "legs": 3, "risk": "limited", "reward": "limited"},
    ])


@router.post("/strategy/calculate")
async def calculate_strategy(request: StrategyRequest):
    legs = [
        StrategyLeg(
            option_type=leg["option_type"],
            action=leg["action"],
            strike=leg["strike"],
            expiry=leg["expiry"],
            quantity=leg.get("quantity", 1),
            premium=leg["premium"],
        )
        for leg in request.legs
    ]
    result = options_service.calculate_strategy(request.name, legs, request.spot)
    return ResponseBase(data={
        "name": result.name,
        "description": result.description,
        "max_profit": result.max_profit,
        "max_loss": result.max_loss,
        "breakeven": result.breakeven,
        "margin_required": result.margin_required,
        "risk_reward_ratio": result.risk_reward_ratio,
        "pnl_at_expiry": result.pnl_at_expiry,
        "legs": [
            {"option_type": l.option_type, "action": l.action, "strike": l.strike,
             "expiry": l.expiry, "quantity": l.quantity, "premium": l.premium}
            for l in result.legs
        ],
    })


@router.get("/indian")
async def list_indian_fno():
    return ResponseBase(data={
        "symbols": [
            {"symbol": "NIFTY", "name": "NIFTY 50", "spot": 24500, "type": "index"},
            {"symbol": "BANKNIFTY", "name": "BANK NIFTY", "spot": 51200, "type": "index"},
            {"symbol": "RELIANCE", "name": "Reliance Industries", "spot": 1250, "type": "stock"},
            {"symbol": "TCS", "name": "Tata Consultancy", "spot": 2090, "type": "stock"},
            {"symbol": "INFY", "name": "Infosys", "spot": 1020, "type": "stock"},
            {"symbol": "SBIN", "name": "State Bank of India", "spot": 994, "type": "stock"},
            {"symbol": "HDFCBANK", "name": "HDFC Bank", "spot": 1700, "type": "stock"},
            {"symbol": "TATAMOTORS", "name": "Tata Motors", "spot": 680, "type": "stock"},
            {"symbol": "ITC", "name": "ITC Ltd", "spot": 460, "type": "stock"},
            {"symbol": "WIPRO", "name": "Wipro", "spot": 280, "type": "stock"},
        ]
    })
