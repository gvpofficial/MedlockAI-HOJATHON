import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, ForeignKey, Text, JSON
from app.database.base import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    event_type = Column(String(100), nullable=False, index=True)
    actor_user_id = Column(String(36), ForeignKey("users.id"), nullable=True)
    actor_role = Column(String(50), nullable=True)
    target_entity = Column(String(100), nullable=False)
    target_id = Column(String(36), nullable=True)
    details_json = Column(JSON, nullable=True)
    prev_hash = Column(String(64), nullable=True)
    sha256_hash = Column(String(64), nullable=False, index=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)
