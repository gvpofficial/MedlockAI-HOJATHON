import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database.base import Base


class Pharmacy(Base):
    __tablename__ = "pharmacies"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), unique=True, nullable=False)
    pharmacy_name = Column(String(255), nullable=False)
    license_number = Column(String(100), unique=True, nullable=False, index=True)
    pharmacy_type = Column(String(50), nullable=False, default="PHYSICAL_CHAIN")  # PHYSICAL_CHAIN, INDEPENDENT, ONLINE
    address = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    user = relationship("User", back_populates="pharmacy_profile")
    dispensing_transactions = relationship("DispensingTransaction", back_populates="pharmacy")
    purchase_attempts = relationship("PurchaseAttempt", back_populates="pharmacy")
