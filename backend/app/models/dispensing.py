import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.database.base import Base


class DispensingTransaction(Base):
    __tablename__ = "dispensing_transactions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    prescription_id = Column(String(36), ForeignKey("prescriptions.id"), nullable=False, index=True)
    prescription_item_id = Column(String(36), ForeignKey("prescription_items.id"), nullable=False)
    pharmacy_id = Column(String(36), ForeignKey("pharmacies.id"), nullable=False, index=True)
    requested_quantity = Column(Integer, nullable=False)
    approved_quantity = Column(Integer, default=0, nullable=False)
    remaining_before = Column(Integer, nullable=False)
    remaining_after = Column(Integer, nullable=False)
    status = Column(String(50), nullable=False, index=True)  # APPROVED, PARTIALLY_APPROVED, REJECTED, ON_HOLD, PHARMACIST_REVIEW_REQUIRED
    rejection_reason = Column(Text, nullable=True)
    transaction_timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    integrity_hash = Column(String(64), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    prescription = relationship("Prescription", back_populates="dispensing_transactions")
    prescription_item = relationship("PrescriptionItem", back_populates="dispensing_transactions")
    pharmacy = relationship("Pharmacy", back_populates="dispensing_transactions")
    risk_event = relationship("RiskEvent", back_populates="transaction", uselist=False)


class PurchaseAttempt(Base):
    __tablename__ = "purchase_attempts"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    prescription_id = Column(String(36), ForeignKey("prescriptions.id"), nullable=False, index=True)
    pharmacy_id = Column(String(36), ForeignKey("pharmacies.id"), nullable=False, index=True)
    requested_quantity = Column(Integer, nullable=False)
    attempt_timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    outcome = Column(String(50), nullable=False)  # APPROVED, REJECTED, HELD, BLOCKED
    ip_address = Column(String(45), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    prescription = relationship("Prescription", back_populates="purchase_attempts")
    pharmacy = relationship("Pharmacy", back_populates="purchase_attempts")
