from fastapi import APIRouter
from pydantic import BaseModel
from app.schemas.common import ResponseBase
from app.stocks.service import stock_service

router = APIRouter()


class StockPriceRequest(BaseModel):
    symbol: str
    market: str = "auto"


class ScanRequest(BaseModel):
    max_price_inr: float = 500
    market: str = "indian"


@router.get("/watched")
async def get_watched_stocks():
    return ResponseBase(data=stock_service.get_watched_stocks())


@router.get("/price/{symbol}")
async def get_stock_price(symbol: str, market: str = "auto"):
    price = await stock_service.get_stock_price(symbol, market)
    if not price:
        return ResponseBase(success=False, error=f"Could not fetch price for {symbol}")
    return ResponseBase(data={
        "symbol": price.symbol,
        "name": price.name,
        "market": price.market,
        "price": str(price.price),
        "currency": price.currency,
        "volume": price.volume,
        "change_pct": str(price.change_pct),
        "timestamp": price.timestamp.isoformat(),
    })


@router.get("/spread/{symbol}")
async def get_bse_nse_spread(symbol: str):
    spread = await stock_service.get_bse_nse_spread(symbol)
    if not spread:
        return ResponseBase(success=False, error=f"Could not calculate spread for {symbol}")
    return ResponseBase(data={
        "symbol": spread.symbol,
        "name": spread.name,
        "nse_price": str(spread.nse_price),
        "bse_price": str(spread.bse_price),
        "spread": str(spread.spread),
        "spread_pct": str(spread.spread_pct),
        "buy_exchange": spread.buy_exchange,
        "sell_exchange": spread.sell_exchange,
        "profitable": spread.profitable,
    })


@router.post("/scan")
async def scan_affordable_stocks(request: ScanRequest):
    prices = await stock_service.scan_affordable_stocks(
        max_price_inr=request.max_price_inr,
        market=request.market,
    )
    return ResponseBase(data={
        "stocks": [
            {
                "symbol": p.symbol,
                "name": p.name,
                "market": p.market,
                "price": str(p.price),
                "currency": p.currency,
                "volume": p.volume,
                "change_pct": str(p.change_pct),
            }
            for p in prices
        ],
        "total": len(prices),
    })


@router.get("/auto-discover")
async def auto_discover_arbitrage(max_price: float = 500):
    spreads = await stock_service.auto_discover_arbitrage(max_price_inr=max_price)
    return ResponseBase(data={
        "opportunities": [
            {
                "symbol": s.symbol,
                "name": s.name,
                "nse_price": str(s.nse_price),
                "bse_price": str(s.bse_price),
                "spread": str(s.spread),
                "spread_pct": str(s.spread_pct),
                "buy_exchange": s.buy_exchange,
                "sell_exchange": s.sell_exchange,
                "profitable": s.profitable,
            }
            for s in spreads
        ],
        "total": len(spreads),
    })
