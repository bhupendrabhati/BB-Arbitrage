import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, Text, Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID
from app.models.user import Base
import enum


class RiskEventType(str, enum.Enum):
    DAILY_LOSS_LIMIT = "daily_loss_limit"
    TRADE_SIZE_LIMIT = "trade_size_limit"
    MAX_OPEN_TRADES = "max_open_trades"
    MAX_TRADES_PER_DAY = "max_trades_per_day"
    STALE_DATA = "stale_data"
    EXCHANGE_UNAVAILABLE = "exchange_unavailable"
    KILL_SWITCH = "kill_switch"
    UNKNOWN_ORDER_STATE = "unknown_order_state"
    CAPITAL_INSUFFICIENT = "capital_insufficient"


class RiskEvent(Base):
    __tablename__ = "risk_events"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    event_type = Column(SAEnum(RiskEventType), nullable=False)
    severity = Column(String(20), default="warning")
    message = Column(Text, nullable=False)
    details_json = Column(Text, default="{}")
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
