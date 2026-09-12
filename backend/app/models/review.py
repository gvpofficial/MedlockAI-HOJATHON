import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.database.base import Base


class ReviewCase(Base):
    __tablename__ = "review_cases"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    case_number = Column(String(50), unique=True, index=True, nullable=False)
    risk_event_id = Column(String(36), ForeignKey("risk_events.id"), unique=True, nullable=False)
    prescription_id = Column(String(36), ForeignKey("prescriptions.id"), nullable=False)
    patient_id = Column(String(36), ForeignKey("patients.id"), nullable=False)
    status = Column(String(50), default="PENDING", index=True)  # PENDING, UNDER_REVIEW, APPROVED_OVERRIDE, CONFIRMED_FRAUD, DISMISSED
    reviewer_id = Column(String(36), ForeignKey("users.id"), nullable=True)
    ai_summary = Column(Text, nullable=True)
    reviewer_notes = Column(Text, nullable=True)
    resolution_timestamp = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    risk_event = relationship("RiskEvent", back_populates="review_case")
    prescription = relationship("Prescription", back_populates="review_cases")
    patient = relationship("Patient", back_populates="review_cases")
    reviewer = relationship("User")
