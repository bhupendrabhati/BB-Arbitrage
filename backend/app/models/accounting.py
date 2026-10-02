import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, Numeric, Text
from sqlalchemy.dialects.postgresql import UUID
from app.models.user import Base


class TaxRecord(Base):
    __tablename__ = "tax_records"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    trade_id = Column(String(100), nullable=False)
    timestamp = Column(DateTime(timezone=True), nullable=False)
    asset = Column(String(20), nullable=False)
    quantity = Column(Numeric(20, 8), nullable=False)
    buy_price = Column(Numeric(20, 8), nullable=False)
    sell_price = Column(Numeric(20, 8), nullable=False)
    fees = Column(Numeric(20, 8), default=0)
    gross_profit = Column(Numeric(20, 8), nullable=False)
    net_profit = Column(Numeric(20, 8), nullable=False)
    exchange = Column(String(100), nullable=False)
    mode = Column(String(20), nullable=False)
    jurisdiction = Column(String(100), nullable=True)
    tax_year = Column(String(4), nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
