from fastapi import APIRouter
from app.schemas.common import ResponseBase

router = APIRouter()


@router.get("/")
async def list_opportunities():
    return ResponseBase(data={"opportunities": [], "total": 0})


@router.get("/{opportunity_id}")
async def get_opportunity(opportunity_id: str):
    return ResponseBase(data={"opportunity_id": opportunity_id})


@router.get("/stats/summary")
async def get_opportunity_stats():
    return ResponseBase(data={"total": 0, "executable": 0, "rejected": 0})
