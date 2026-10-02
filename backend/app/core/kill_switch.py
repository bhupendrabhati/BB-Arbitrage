import asyncio
from datetime import datetime, timezone
from app.core.logging import get_logger

logger = get_logger("kill_switch")


class KillSwitch:
    def __init__(self):
        self._active = False
        self._activated_at: datetime | None = None
        self._reason: str = ""
        self._lock = asyncio.Lock()

    @property
    def is_active(self) -> bool:
        return self._active

    @property
    def activated_at(self) -> datetime | None:
        return self._activated_at

    @property
    def reason(self) -> str:
        return self._reason

    async def activate(self, reason: str = "Manual activation") -> None:
        async with self._lock:
            self._active = True
            self._activated_at = datetime.now(timezone.utc)
            self._reason = reason
            logger.warning("kill_switch_activated", reason=reason)

    async def deactivate(self) -> None:
        async with self._lock:
            self._active = False
            self._activated_at = None
            self._reason = ""
            logger.info("kill_switch_deactivated")

    async def check(self) -> None:
        if self._active:
            from app.core.exceptions import KillSwitchActiveError
            raise KillSwitchActiveError(f"Kill switch active: {self._reason}")


kill_switch = KillSwitch()
