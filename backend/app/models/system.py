import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID
from app.models.user import Base


class SystemEvent(Base):
    __tablename__ = "system_events"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    event_type = Column(String(50), nullable=False)
    message = Column(Text, nullable=False)
    details_json = Column(Text, default="{}")
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
