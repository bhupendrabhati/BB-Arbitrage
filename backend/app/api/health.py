from fastapi import APIRouter
from app.schemas.common import ResponseBase
from app.config.settings import settings
from app.core.kill_switch import kill_switch

router = APIRouter()


@router.get("/")
async def health_check():
    return ResponseBase(data={
        "status": "healthy",
        "version": "1.0.0",
        "mode": settings.TRADING_MODE.value,
        "live_trading_enabled": settings.LIVE_TRADING_ENABLED,
        "kill_switch_active": kill_switch.is_active,
    })


@router.get("/ready")
async def readiness_check():
    return ResponseBase(data={"ready": True})
