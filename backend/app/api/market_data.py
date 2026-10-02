from fastapi import APIRouter
from app.schemas.common import ResponseBase

router = APIRouter()


@router.get("/status")
async def get_market_data_status():
    return ResponseBase(
        data={"status": "active", "exchanges": [], "symbols": []}
    )


@router.get("/tickers/{symbol}")
async def get_tickers(symbol: str):
    return ResponseBase(data={"symbol": symbol, "tickers": {}})


@router.get("/order-book/{exchange}/{symbol}")
async def get_order_book(exchange: str, symbol: str):
    return ResponseBase(data={"exchange": exchange, "symbol": symbol, "order_book": {}})
