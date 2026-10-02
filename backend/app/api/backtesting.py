from fastapi import APIRouter
from app.schemas.common import ResponseBase

router = APIRouter()


@router.get("/runs")
async def list_backtest_runs():
    return ResponseBase(data={"runs": [], "total": 0})


@router.post("/run")
async def run_backtest():
    return ResponseBase(data={"message": "Backtest endpoint - upload CSV data to run"})


@router.get("/runs/{run_id}")
async def get_backtest_run(run_id: str):
    return ResponseBase(data={"run_id": run_id})
