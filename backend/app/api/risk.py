from fastapi import APIRouter
from pydantic import BaseModel
from app.schemas.common import ResponseBase
from app.core.kill_switch import kill_switch

router = APIRouter()


class KillSwitchRequest(BaseModel):
    reason: str = "Manual activation"


@router.get("/status")
async def get_risk_status():
    return ResponseBase(data={
        "daily_pnl": "0",
        "daily_trades": 0,
        "open_trades": 0,
        "total_exposure": "0",
        "daily_loss_limit": "-2",
        "max_open_trades": 1,
        "max_trades_per_day": 5,
        "kill_switch_active": kill_switch.is_active,
    })


@router.post("/kill-switch")
async def activate_kill_switch(request: KillSwitchRequest):
    await kill_switch.activate(reason=request.reason)
    return ResponseBase(data={"active": True, "reason": request.reason})


@router.delete("/kill-switch")
async def deactivate_kill_switch():
    await kill_switch.deactivate()
    return ResponseBase(data={"active": False})


@router.get("/kill-switch")
async def get_kill_switch_status():
    return ResponseBase(data={
        "active": kill_switch.is_active,
        "activated_at": kill_switch.activated_at.isoformat() if kill_switch.activated_at else None,
        "reason": kill_switch.reason,
    })
