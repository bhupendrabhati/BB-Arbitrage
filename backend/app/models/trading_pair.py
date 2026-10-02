import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Numeric
from sqlalchemy.dialects.postgresql import UUID
from app.models.user import Base


class TradingPair(Base):
    __tablename__ = "trading_pairs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    exchange_id = Column(UUID(as_uuid=True), ForeignKey("exchanges.id"), nullable=False)
    symbol = Column(String(20), nullable=False)
    base_asset = Column(String(10), nullable=False)
    quote_asset = Column(String(10), nullable=False)
    is_active = Column(Boolean, default=True)
    min_order_size = Column(Numeric(20, 8), default=0)
    max_order_size = Column(Numeric(20, 8), default=0)
    tick_size = Column(Numeric(20, 8), default=0.01)
    lot_size = Column(Numeric(20, 8), default=0.001)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
