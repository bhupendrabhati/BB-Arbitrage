from fastapi import APIRouter
from app.schemas.common import ResponseBase

router = APIRouter()


@router.get("/status")
async def get_trading_status():
    return ResponseBase(data={"mode": "paper", "active": True})


@router.get("/trades")
async def list_trades():
    return ResponseBase(data={"trades": [], "total": 0})


@router.post("/execute")
async def execute_trade():
    return ResponseBase(data={"message": "Paper trading mode - no live execution"})


@router.get("/trades/{trade_id}")
async def get_trade(trade_id: str):
    return ResponseBase(data={"trade_id": trade_id})
