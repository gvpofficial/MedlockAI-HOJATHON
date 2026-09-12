import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Boolean, Integer, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.database.base import Base


class Prescription(Base):
    __tablename__ = "prescriptions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    prescription_code = Column(String(50), unique=True, index=True, nullable=False)
    patient_id = Column(String(36), ForeignKey("patients.id"), nullable=False)
    doctor_id = Column(String(36), ForeignKey("doctors.id"), nullable=False)
    issue_date = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    expiry_date = Column(DateTime, nullable=False)
    status = Column(String(50), default="ACTIVE", index=True)  # ACTIVE, EXHAUSTED, EXPIRED, CANCELLED, SUSPENDED
    qr_code_data = Column(Text, nullable=True)
    digital_signature = Column(String(512), nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    patient = relationship("Patient", back_populates="prescriptions")
    doctor = relationship("Doctor", back_populates="prescriptions")
    items = relationship("PrescriptionItem", back_populates="prescription", cascade="all, delete-orphan")
    dispensing_transactions = relationship("DispensingTransaction", back_populates="prescription")
    purchase_attempts = relationship("PurchaseAttempt", back_populates="prescription")
    risk_events = relationship("RiskEvent", back_populates="prescription")
    review_cases = relationship("ReviewCase", back_populates="prescription")


class PrescriptionItem(Base):
    __tablename__ = "prescription_items"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    prescription_id = Column(String(36), ForeignKey("prescriptions.id"), nullable=False)
    medicine_name = Column(String(255), nullable=False)
    medicine_code = Column(String(100), nullable=True)  # NDC / RxNorm code
    is_restricted = Column(Boolean, default=True)
    authorized_quantity = Column(Integer, nullable=False)
    remaining_quantity = Column(Integer, nullable=False)
    dosage_instructions = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    prescription = relationship("Prescription", back_populates="items")
    dispensing_transactions = relationship("DispensingTransaction", back_populates="prescription_item")
