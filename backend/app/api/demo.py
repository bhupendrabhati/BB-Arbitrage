from fastapi import APIRouter
from app.schemas.common import ResponseBase

router = APIRouter()


@router.post("/start")
async def start_demo():
    import asyncio
    from app.demo import run_demo

    asyncio.create_task(run_demo())
    return ResponseBase(data={"status": "started", "message": "Demo mode activated. Market data is being simulated."})


@router.get("/opportunities")
async def get_demo_opportunities():
    from app.demo import get_all_opportunities
    opps = get_all_opportunities()
    return ResponseBase(data={"opportunities": opps, "total": len(opps)})


@router.get("/portfolio")
async def get_demo_portfolio():
    from app.paper_trading.engine import paper_trading_engine
    from app.portfolio.tracker import portfolio_tracker
    from app.risk.manager import risk_manager

    paper_status = paper_trading_engine.get_status()
    portfolio_summary = portfolio_tracker.get_summary()
    risk_status = risk_manager.get_status()

    return ResponseBase(data={
        "paper_trading": paper_status,
        "portfolio": portfolio_summary,
        "risk": risk_status,
    })
