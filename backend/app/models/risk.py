import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Text, JSON, Boolean
from sqlalchemy.orm import relationship
from app.database.base import Base


class RiskEvent(Base):
    __tablename__ = "risk_events"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    transaction_id = Column(String(36), ForeignKey("dispensing_transactions.id"), nullable=True)
    prescription_id = Column(String(36), ForeignKey("prescriptions.id"), nullable=False)
    patient_id = Column(String(36), ForeignKey("patients.id"), nullable=False)
    risk_score = Column(Integer, nullable=False)  # 0 - 100
    risk_level = Column(String(50), nullable=False)  # LOW, MEDIUM, HIGH, CRITICAL
    factors_json = Column(JSON, nullable=True)
    agent_summary = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    transaction = relationship("DispensingTransaction", back_populates="risk_event")
    prescription = relationship("Prescription", back_populates="risk_events")
    review_case = relationship("ReviewCase", back_populates="risk_event", uselist=False)


class Warning(Base):
    __tablename__ = "warnings"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    patient_id = Column(String(36), ForeignKey("patients.id"), nullable=False, index=True)
    prescription_id = Column(String(36), ForeignKey("prescriptions.id"), nullable=True)
    severity = Column(String(50), default="WARNING")  # INFO, WARNING, CRITICAL
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    patient = relationship("Patient", back_populates="warnings")
