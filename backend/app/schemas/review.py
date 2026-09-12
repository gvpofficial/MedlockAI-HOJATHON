from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, ConfigDict


class WarningResponse(BaseModel):
    id: str
    patient_id: str
    prescription_id: Optional[str] = None
    severity: str
    title: str
    message: str
    is_read: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ReviewCaseResponse(BaseModel):
    id: str
    case_number: str
    risk_event_id: str
    prescription_id: str
    prescription_code: Optional[str] = None
    patient_id: str
    patient_name: Optional[str] = None
    status: str
    risk_score: Optional[int] = None
    risk_level: Optional[str] = None
    ai_summary: Optional[str] = None
    reviewer_notes: Optional[str] = None
    resolution_timestamp: Optional[datetime] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ReviewCaseResolveRequest(BaseModel):
    resolution: str  # APPROVED_OVERRIDE, CONFIRMED_FRAUD, DISMISSED
    reviewer_notes: str


class AuditLogResponse(BaseModel):
    id: str
    event_type: str
    actor_user_id: Optional[str] = None
    actor_role: Optional[str] = None
    target_entity: str
    target_id: Optional[str] = None
    details_json: Optional[Dict[str, Any]] = None
    prev_hash: Optional[str] = None
    sha256_hash: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class SystemStatsResponse(BaseModel):
    total_prescriptions: int
    active_prescriptions: int
    total_dispensing_transactions: int
    prevented_excess_dispenses: int
    pending_review_cases: int
    active_pharmacies: int
    active_doctors: int
    active_patients: int
