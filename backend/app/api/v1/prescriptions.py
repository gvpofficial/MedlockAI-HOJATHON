from datetime import datetime, timedelta, timezone
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.api.deps import get_current_user, RoleChecker
from app.core.audit import log_audit_event
from app.core.prescription_utils import (
    generate_prescription_code,
    generate_digital_signature,
    generate_qr_code_base64
)
from app.models.user import User
from app.models.patient import Patient
from app.models.doctor import Doctor
from app.models.prescription import Prescription, PrescriptionItem
from app.models.dispensing import DispensingTransaction
from app.schemas.prescription import (
    PrescriptionCreate,
    PrescriptionResponse,
    PrescriptionItemResponse
)

router = APIRouter(prefix="/prescriptions", tags=["Prescriptions"])


def _format_prescription(p: Prescription, db: Session) -> PrescriptionResponse:
    # Query remaining quantity dynamically from central ledger
    items_response = []
    for item in p.items:
        dispensed = (
            db.query(func.coalesce(func.sum(DispensingTransaction.approved_quantity), 0))
            .filter(
                DispensingTransaction.prescription_item_id == item.id,
                DispensingTransaction.status.in_(["APPROVED", "PARTIALLY_APPROVED"])
            )
            .scalar()
        ) or 0
        rem = max(0, item.authorized_quantity - int(dispensed))
        items_response.append(
            PrescriptionItemResponse(
                id=item.id,
                medicine_name=item.medicine_name,
                medicine_code=item.medicine_code,
                is_restricted=item.is_restricted,
                authorized_quantity=item.authorized_quantity,
                remaining_quantity=rem,
                dosage_instructions=item.dosage_instructions,
                created_at=item.created_at
            )
        )

    return PrescriptionResponse(
        id=p.id,
        prescription_code=p.prescription_code,
        patient_id=p.patient_id,
        patient_name=p.patient.user.full_name if p.patient and p.patient.user else "Unknown Patient",
        doctor_id=p.doctor_id,
        doctor_name=p.doctor.user.full_name if p.doctor and p.doctor.user else "Unknown Doctor",
        hospital_name=p.doctor.hospital_clinic_name if p.doctor else None,
        issue_date=p.issue_date,
        expiry_date=p.expiry_date,
        status=p.status,
        qr_code_data=p.qr_code_data,
        digital_signature=p.digital_signature,
        notes=p.notes,
        items=items_response,
        created_at=p.created_at,
        updated_at=p.updated_at
    )


@router.post("", response_model=PrescriptionResponse)
def create_prescription(
    req: PrescriptionCreate,
    db: Session = Depends(get_db),
    user: User = Depends(RoleChecker(["DOCTOR", "ADMIN"]))
):
    # Verify doctor profile
    doctor = user.doctor_profile
    if not doctor and user.role != "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Doctor profile not found for this user."
        )
    
    # If admin creates, pick first doctor or reject
    doctor_id = doctor.id if doctor else (db.query(Doctor).first().id)

    # Verify patient exists
    patient = db.query(Patient).filter(Patient.id == req.patient_id).first()
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found in system."
        )

    if not req.items or len(req.items) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Prescription must contain at least one medicine item."
        )

    now = datetime.now(timezone.utc)
    expiry = now + timedelta(days=req.expiry_days)
    code = generate_prescription_code()

    # Generate cryptographic signature
    items_raw = [item.dict() for item in req.items]
    signature = generate_digital_signature(
        doctor_id=doctor_id,
        patient_id=patient.id,
        items=items_raw,
        issue_date=now.isoformat()
    )

    # Generate QR Code Payload
    qr_payload = f"MEDLOCK_RX:{code}:{patient.id}:{signature[:16]}"
    qr_base64 = generate_qr_code_base64(qr_payload)

    # Create Prescription
    prescription = Prescription(
        prescription_code=code,
        patient_id=patient.id,
        doctor_id=doctor_id,
        issue_date=now,
        expiry_date=expiry,
        status="ACTIVE",
        qr_code_data=qr_base64,
        digital_signature=signature,
        notes=req.notes
    )
    db.add(prescription)
    db.flush()

    # Create Items
    for item in req.items:
        med_code = item.medicine_code or f"NDC-{item.medicine_name[:3].upper()}-9901"
        p_item = PrescriptionItem(
            prescription_id=prescription.id,
            medicine_name=item.medicine_name.strip(),
            medicine_code=med_code,
            is_restricted=item.is_restricted,
            authorized_quantity=item.authorized_quantity,
            remaining_quantity=item.authorized_quantity,
            dosage_instructions=item.dosage_instructions
        )
        db.add(p_item)

    db.commit()
    db.refresh(prescription)

    # Log audit
    log_audit_event(
        db=db,
        event_type="PRESCRIPTION_CREATED",
        target_entity="prescriptions",
        target_id=prescription.id,
        actor_user_id=user.id,
        actor_role=user.role,
        details={
            "prescription_code": code,
            "patient_id": patient.id,
            "items_count": len(req.items),
            "signature": signature
        }
    )

    return _format_prescription(prescription, db)


@router.get("", response_model=List[PrescriptionResponse])
def list_prescriptions(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    query = db.query(Prescription)
    
    if user.role == "PATIENT" and user.patient_profile:
        query = query.filter(Prescription.patient_id == user.patient_profile.id)
    elif user.role == "DOCTOR" and user.doctor_profile:
        query = query.filter(Prescription.doctor_id == user.doctor_profile.id)
    # PHARMACY and ADMIN see all prescriptions (or can look up by code)

    prescriptions = query.order_by(Prescription.created_at.desc()).all()
    return [_format_prescription(p, db) for p in prescriptions]


@router.get("/{id}", response_model=PrescriptionResponse)
def get_prescription(
    id: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    p = db.query(Prescription).filter(Prescription.id == id).first()
    if not p:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prescription not found."
        )

    # Authorization checks
    if user.role == "PATIENT" and user.patient_profile and p.patient_id != user.patient_profile.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied.")
    if user.role == "DOCTOR" and user.doctor_profile and p.doctor_id != user.doctor_profile.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied.")

    return _format_prescription(p, db)


@router.get("/code/{code}", response_model=PrescriptionResponse)
def get_prescription_by_code(
    code: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    clean_code = code.strip()
    # Strip potential QR prefix if scanned directly
    if clean_code.startswith("MEDLOCK_RX:"):
        parts = clean_code.split(":")
        if len(parts) >= 2:
            clean_code = parts[1]

    p = db.query(Prescription).filter(Prescription.prescription_code == clean_code).first()
    if not p:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Prescription with code '{clean_code}' not found."
        )

    return _format_prescription(p, db)


@router.post("/{id}/cancel", response_model=PrescriptionResponse)
def cancel_prescription(
    id: str,
    db: Session = Depends(get_db),
    user: User = Depends(RoleChecker(["DOCTOR", "ADMIN"]))
):
    p = db.query(Prescription).filter(Prescription.id == id).first()
    if not p:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Prescription not found.")

    if user.role == "DOCTOR" and user.doctor_profile and p.doctor_id != user.doctor_profile.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cannot cancel another doctor's prescription.")

    p.status = "CANCELLED"
    p.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(p)

    log_audit_event(
        db=db,
        event_type="PRESCRIPTION_CANCELLED",
        target_entity="prescriptions",
        target_id=p.id,
        actor_user_id=user.id,
        actor_role=user.role,
        details={"prescription_code": p.prescription_code}
    )

    return _format_prescription(p, db)
