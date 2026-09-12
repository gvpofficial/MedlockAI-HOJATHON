from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict


class PrescriptionItemCreate(BaseModel):
    medicine_name: str
    medicine_code: Optional[str] = None
    is_restricted: bool = True
    authorized_quantity: int
    dosage_instructions: Optional[str] = None


class PrescriptionItemResponse(BaseModel):
    id: str
    medicine_name: str
    medicine_code: Optional[str] = None
    is_restricted: bool
    authorized_quantity: int
    remaining_quantity: int
    dosage_instructions: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PrescriptionCreate(BaseModel):
    patient_id: str
    expiry_days: int = 30  # Default 30 days validity
    notes: Optional[str] = None
    items: List[PrescriptionItemCreate]


class PrescriptionResponse(BaseModel):
    id: str
    prescription_code: str
    patient_id: str
    patient_name: Optional[str] = None
    doctor_id: str
    doctor_name: Optional[str] = None
    hospital_name: Optional[str] = None
    issue_date: datetime
    expiry_date: datetime
    status: str
    qr_code_data: Optional[str] = None
    digital_signature: Optional[str] = None
    notes: Optional[str] = None
    items: List[PrescriptionItemResponse] = []
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
