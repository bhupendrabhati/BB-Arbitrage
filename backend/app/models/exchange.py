import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Boolean, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID
from app.models.user import Base


class Exchange(Base):
    __tablename__ = "exchanges"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), unique=True, nullable=False)
    display_name = Column(String(200), nullable=False)
    is_active = Column(Boolean, default=True)
    api_base_url = Column(String(500), nullable=False)
    ws_url = Column(String(500), nullable=True)
    supports_spot = Column(Boolean, default=True)
    supports_futures = Column(Boolean, default=False)
    fee_maker = Column(String(20), default="0.001")
    fee_taker = Column(String(20), default="0.001")
    config_json = Column(Text, default="{}")
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
