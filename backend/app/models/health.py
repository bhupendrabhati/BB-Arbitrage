import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, Boolean, Text
from sqlalchemy.dialects.postgresql import UUID
from app.models.user import Base


class APIHealth(Base):
    __tablename__ = "api_health"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    exchange = Column(String(100), nullable=False)
    is_healthy = Column(Boolean, default=True)
    latency_ms = Column(String(20), nullable=True)
    last_check = Column(DateTime(timezone=True), nullable=False)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
