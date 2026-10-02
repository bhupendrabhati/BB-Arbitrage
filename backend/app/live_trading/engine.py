from app.core.logging import get_logger
from app.config.settings import settings

logger = get_logger("live_trading")


class LiveTradingEngine:
    def __init__(self):
        self._enabled = settings.LIVE_TRADING_ENABLED
        if not self._enabled:
            logger.warning("live_trading_disabled")

    async def execute_trade(self, trade_request: dict) -> dict:
        if not self._enabled:
            logger.error("live_trading_attempt_when_disabled")
            return {"success": False, "error": "Live trading is disabled. Enable LIVE_TRADING_ENABLED to use."}

        logger.warning("live_trade_attempt", trade_request=trade_request)
        return {"success": False, "error": "Live trading not implemented in v1"}


live_trading_engine = LiveTradingEngine()
