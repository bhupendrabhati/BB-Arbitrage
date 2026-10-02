from fastapi import APIRouter
from app.schemas.common import ResponseBase

router = APIRouter()


@router.get("/")
async def get_portfolio():
    return ResponseBase(data={
        "initial_capital": "100",
        "current_capital": "100",
        "total_pnl": "0",
        "total_trades": 0,
        "winning_trades": 0,
        "losing_trades": 0,
        "win_rate": "0",
        "max_drawdown": "0",
    })


@router.get("/trades")
async def get_portfolio_trades():
    return ResponseBase(data={"trades": [], "total": 0})


@router.get("/performance")
async def get_performance():
    return ResponseBase(data={"daily": [], "summary": {}})
