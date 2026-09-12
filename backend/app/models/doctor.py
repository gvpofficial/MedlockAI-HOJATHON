import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database.base import Base


class Doctor(Base):
    __tablename__ = "doctors"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), unique=True, nullable=False)
    license_number = Column(String(100), unique=True, nullable=False, index=True)
    specialization = Column(String(150), nullable=True)
    hospital_clinic_name = Column(String(255), nullable=True)
    is_verified = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    user = relationship("User", back_populates="doctor_profile")
    prescriptions = relationship("Prescription", back_populates="doctor")
