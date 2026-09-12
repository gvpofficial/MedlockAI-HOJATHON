from datetime import datetime, timezone
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.api.deps import get_current_user, RoleChecker
from app.core.audit import log_audit_event
from app.models.user import User
from app.models.patient import Patient
from app.models.doctor import Doctor
from app.models.pharmacy import Pharmacy
from app.models.prescription import Prescription
from app.models.dispensing import DispensingTransaction
from app.models.risk import RiskEvent, Warning
from app.models.review import ReviewCase
from app.models.audit import AuditLog
from app.schemas.review import (
    ReviewCaseResponse,
    ReviewCaseResolveRequest,
    AuditLogResponse,
    WarningResponse,
    SystemStatsResponse
)

router = APIRouter(prefix="/reviews", tags=["Review & Admin"])


@router.get("/cases", response_model=List[ReviewCaseResponse])
def list_review_cases(
    status_filter: Optional[str] = None,
    db: Session = Depends(get_db),
    user: User = Depends(RoleChecker(["ADMIN", "PHARMACY", "DOCTOR"]))
):
    query = db.query(ReviewCase)
    if status_filter:
        query = query.filter(ReviewCase.status == status_filter.upper())
        
    cases = query.order_by(ReviewCase.created_at.desc()).all()
    
    res = []
    for c in cases:
        p_name = c.patient.user.full_name if c.patient and c.patient.user else "Unknown Patient"
        p_code = c.prescription.prescription_code if c.prescription else "Unknown Rx"
        r_score = c.risk_event.risk_score if c.risk_event else 0
        r_level = c.risk_event.risk_level if c.risk_event else "UNKNOWN"
        
        res.append(
            ReviewCaseResponse(
                id=c.id,
                case_number=c.case_number,
                risk_event_id=c.risk_event_id,
                prescription_id=c.prescription_id,
                prescription_code=p_code,
                patient_id=c.patient_id,
                patient_name=p_name,
                status=c.status,
                risk_score=r_score,
                risk_level=r_level,
                ai_summary=c.ai_summary,
                reviewer_notes=c.reviewer_notes,
                resolution_timestamp=c.resolution_timestamp,
                created_at=c.created_at
            )
        )
    return res


@router.get("/cases/{id}", response_model=ReviewCaseResponse)
def get_review_case(
    id: str,
    db: Session = Depends(get_db),
    user: User = Depends(RoleChecker(["ADMIN", "PHARMACY", "DOCTOR"]))
):
    c = db.query(ReviewCase).filter(ReviewCase.id == id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Review case not found.")

    p_name = c.patient.user.full_name if c.patient and c.patient.user else "Unknown Patient"
    p_code = c.prescription.prescription_code if c.prescription else "Unknown Rx"
    r_score = c.risk_event.risk_score if c.risk_event else 0
    r_level = c.risk_event.risk_level if c.risk_event else "UNKNOWN"

    return ReviewCaseResponse(
        id=c.id,
        case_number=c.case_number,
        risk_event_id=c.risk_event_id,
        prescription_id=c.prescription_id,
        prescription_code=p_code,
        patient_id=c.patient_id,
        patient_name=p_name,
        status=c.status,
        risk_score=r_score,
        risk_level=r_level,
        ai_summary=c.ai_summary,
        reviewer_notes=c.reviewer_notes,
        resolution_timestamp=c.resolution_timestamp,
        created_at=c.created_at
    )


@router.post("/cases/{id}/resolve", response_model=ReviewCaseResponse)
def resolve_review_case(
    id: str,
    req: ReviewCaseResolveRequest,
    db: Session = Depends(get_db),
    user: User = Depends(RoleChecker(["ADMIN", "PHARMACY"]))
):
    c = db.query(ReviewCase).filter(ReviewCase.id == id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Review case not found.")

    valid_statuses = ["APPROVED_OVERRIDE", "CONFIRMED_FRAUD", "DISMISSED"]
    if req.resolution not in valid_statuses:
        raise HTTPException(status_code=400, detail=f"Invalid resolution. Must be one of: {valid_statuses}")

    now = datetime.now(timezone.utc)
    c.status = req.resolution
    c.reviewer_id = user.id
    c.reviewer_notes = req.reviewer_notes
    c.resolution_timestamp = now

    # If APPROVED_OVERRIDE, update the associated transaction status
    if req.resolution == "APPROVED_OVERRIDE" and c.risk_event and c.risk_event.transaction_id:
        tx = db.query(DispensingTransaction).filter(DispensingTransaction.id == c.risk_event.transaction_id).first()
        if tx and tx.status == "ON_HOLD":
            tx.status = "APPROVED"
            tx.approved_quantity = tx.requested_quantity
            tx.remaining_after = max(0, tx.remaining_before - tx.approved_quantity)

    # If CONFIRMED_FRAUD, suspend prescription
    if req.resolution == "CONFIRMED_FRAUD" and c.prescription:
        c.prescription.status = "SUSPENDED"

    db.commit()
    db.refresh(c)

    log_audit_event(
        db=db,
        event_type="REVIEW_CASE_RESOLVED",
        target_entity="review_cases",
        target_id=c.id,
        actor_user_id=user.id,
        actor_role=user.role,
        details={
            "case_number": c.case_number,
            "resolution": req.resolution,
            "notes": req.reviewer_notes
        }
    )

    p_name = c.patient.user.full_name if c.patient and c.patient.user else "Unknown Patient"
    p_code = c.prescription.prescription_code if c.prescription else "Unknown Rx"
    r_score = c.risk_event.risk_score if c.risk_event else 0
    r_level = c.risk_event.risk_level if c.risk_event else "UNKNOWN"

    return ReviewCaseResponse(
        id=c.id,
        case_number=c.case_number,
        risk_event_id=c.risk_event_id,
        prescription_id=c.prescription_id,
        prescription_code=p_code,
        patient_id=c.patient_id,
        patient_name=p_name,
        status=c.status,
        risk_score=r_score,
        risk_level=r_level,
        ai_summary=c.ai_summary,
        reviewer_notes=c.reviewer_notes,
        resolution_timestamp=c.resolution_timestamp,
        created_at=c.created_at
    )


@router.get("/audit-logs", response_model=List[AuditLogResponse])
def get_audit_logs(
    limit: int = 50,
    db: Session = Depends(get_db),
    user: User = Depends(RoleChecker(["ADMIN", "PHARMACY"]))
):
    logs = db.query(AuditLog).order_by(AuditLog.created_at.desc()).limit(limit).all()
    return logs


@router.get("/warnings", response_model=List[WarningResponse])
def get_patient_warnings(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    query = db.query(Warning)
    if user.role == "PATIENT" and user.patient_profile:
        query = query.filter(Warning.patient_id == user.patient_profile.id)
    
    warnings = query.order_by(Warning.created_at.desc()).limit(20).all()
    return warnings


@router.get("/stats", response_model=SystemStatsResponse)
def get_system_stats(
    db: Session = Depends(get_db)
):
    total_rx = db.query(Prescription).count()
    active_rx = db.query(Prescription).filter(Prescription.status == "ACTIVE").count()
    total_tx = db.query(DispensingTransaction).count()
    
    # Count prevented over-dispenses (REJECTED and ON_HOLD transactions)
    prevented = db.query(DispensingTransaction).filter(
        DispensingTransaction.status.in_(["REJECTED", "ON_HOLD"])
    ).count()
    
    pending_cases = db.query(ReviewCase).filter(ReviewCase.status == "PENDING").count()
    pharmacies_cnt = db.query(Pharmacy).count()
    doctors_cnt = db.query(Doctor).count()
    patients_cnt = db.query(Patient).count()

    return SystemStatsResponse(
        total_prescriptions=total_rx,
        active_prescriptions=active_rx,
        total_dispensing_transactions=total_tx,
        prevented_excess_dispenses=prevented,
        pending_review_cases=pending_cases,
        active_pharmacies=pharmacies_cnt,
        active_doctors=doctors_cnt,
        active_patients=patients_cnt
    )
