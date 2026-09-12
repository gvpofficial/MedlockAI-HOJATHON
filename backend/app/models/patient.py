import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, ForeignKey, Date
from sqlalchemy.orm import relationship
from app.database.base import Base


class Patient(Base):
    __tablename__ = "patients"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), unique=True, nullable=False)
    date_of_birth = Column(Date, nullable=True)
    national_id_hash = Column(String(64), nullable=True, index=True)
    emergency_contact = Column(String(100), nullable=True)
    blood_group = Column(String(10), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    user = relationship("User", back_populates="patient_profile")
    prescriptions = relationship("Prescription", back_populates="patient", cascade="all, delete-orphan")
    warnings = relationship("Warning", back_populates="patient", cascade="all, delete-orphan")
    review_cases = relationship("ReviewCase", back_populates="patient")
