from app.core.logging import get_logger
from app.config.settings import settings

logger = get_logger("notifications")


class NotificationService:
    def __init__(self):
        self._enabled = bool(settings.TELEGRAM_BOT_TOKEN or settings.SMTP_HOST)

    async def send_alert(self, alert_type: str, message: str, details: dict | None = None) -> bool:
        if not self._enabled:
            logger.debug("notification_skipped", type=alert_type, reason="notifications_disabled")
            return False

        logger.info("notification_sent", type=alert_type, message=message)

        if settings.TELEGRAM_BOT_TOKEN:
            await self._send_telegram(alert_type, message)

        if settings.SMTP_HOST:
            await self._send_email(alert_type, message)

        return True

    async def _send_telegram(self, alert_type: str, message: str) -> None:
        logger.info("telegram_alert", type=alert_type, message=message)

    async def _send_email(self, alert_type: str, message: str) -> None:
        logger.info("email_alert", type=alert_type, message=message)

    async def notify_opportunity(self, symbol: str, net_profit: str) -> None:
        await self.send_alert("opportunity", f"New opportunity: {symbol} - Expected profit: {net_profit}")

    async def notify_trade_executed(self, trade_id: str, net_profit: str) -> None:
        await self.send_alert("trade_executed", f"Trade executed: {trade_id} - P&L: {net_profit}")

    async def notify_trade_rejected(self, reason: str) -> None:
        await self.send_alert("trade_rejected", f"Trade rejected: {reason}")

    async def notify_daily_loss_limit(self) -> None:
        await self.send_alert("daily_loss_limit", "Daily loss limit reached. Trading stopped.")

    async def notify_kill_switch(self, reason: str) -> None:
        await self.send_alert("kill_switch", f"Kill switch activated: {reason}")

    async def notify_exchange_disconnected(self, exchange: str) -> None:
        await self.send_alert("exchange_disconnected", f"Exchange disconnected: {exchange}")


notification_service = NotificationService()
