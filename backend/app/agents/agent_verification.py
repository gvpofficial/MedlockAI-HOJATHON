from datetime import datetime, timezone
from typing import Optional
from sqlalchemy.orm import Session
from app.models.prescription import Prescription, PrescriptionItem
from app.models.doctor import Doctor
from app.models.patient import Patient
from app.schemas.agent import VerificationAgentResult


def run_prescription_verification_agent(
    db: Session,
    prescription_code: str,
    medicine_name: Optional[str] = None,
    prescription_item_id: Optional[str] = None
) -> (VerificationAgentResult, Optional[Prescription], Optional[PrescriptionItem]):
    now = datetime.now(timezone.utc)
    
    # 1. Look up prescription
    prescription = (
        db.query(Prescription)
        .filter(Prescription.prescription_code == prescription_code.strip())
        .first()
    )
    
    if not prescription:
        return VerificationAgentResult(
            valid=False,
            prescription_status="NOT_FOUND",
            expiry_valid=False,
            doctor_verified=False,
            patient_verified=False,
            medicine_match=False,
            rejection_reason=f"Prescription with code '{prescription_code}' does not exist in central registry.",
            timestamp=now
        ), None, None

    # 2. Check Prescription Status
    if prescription.status != "ACTIVE":
        return VerificationAgentResult(
            valid=False,
            prescription_id=prescription.id,
            prescription_code=prescription.prescription_code,
            prescription_status=prescription.status,
            expiry_valid=True,
            doctor_verified=True,
            patient_verified=True,
            medicine_match=True,
            rejection_reason=f"Prescription status is {prescription.status}. Cannot dispense against non-active prescription.",
            timestamp=now
        ), prescription, None

    # 3. Check Expiry
    # Ensure timezone-aware comparison
    expiry = prescription.expiry_date
    if expiry.tzinfo is None:
        expiry = expiry.replace(tzinfo=timezone.utc)
    expiry_valid = expiry >= now
    if not expiry_valid:
        return VerificationAgentResult(
            valid=False,
            prescription_id=prescription.id,
            prescription_code=prescription.prescription_code,
            prescription_status="EXPIRED",
            expiry_valid=False,
            doctor_verified=True,
            patient_verified=True,
            medicine_match=True,
            rejection_reason=f"Prescription expired on {expiry.strftime('%Y-%m-%d %H:%M UTC')}.",
            timestamp=now
        ), prescription, None

    # 4. Check Doctor Status
    doctor = db.query(Doctor).filter(Doctor.id == prescription.doctor_id).first()
    doctor_verified = doctor is not None and doctor.is_verified
    if not doctor_verified:
        return VerificationAgentResult(
            valid=False,
            prescription_id=prescription.id,
            prescription_code=prescription.prescription_code,
            prescription_status=prescription.status,
            expiry_valid=True,
            doctor_verified=False,
            patient_verified=True,
            medicine_match=True,
            rejection_reason="Prescribing physician could not be verified in the medical registry.",
            timestamp=now
        ), prescription, None

    # 5. Check Patient Identity
    patient = db.query(Patient).filter(Patient.id == prescription.patient_id).first()
    patient_verified = patient is not None
    if not patient_verified:
        return VerificationAgentResult(
            valid=False,
            prescription_id=prescription.id,
            prescription_code=prescription.prescription_code,
            prescription_status=prescription.status,
            expiry_valid=True,
            doctor_verified=True,
            patient_verified=False,
            medicine_match=True,
            rejection_reason="Patient record missing from central repository.",
            timestamp=now
        ), prescription, None

    # 6. Check Medicine Item Match
    target_item = None
    if prescription_item_id:
        target_item = (
            db.query(PrescriptionItem)
            .filter(
                PrescriptionItem.id == prescription_item_id,
                PrescriptionItem.prescription_id == prescription.id
            )
            .first()
        )
    elif medicine_name:
        target_item = (
            db.query(PrescriptionItem)
            .filter(
                PrescriptionItem.prescription_id == prescription.id,
                PrescriptionItem.medicine_name.ilike(f"%{medicine_name.strip()}%")
            )
            .first()
        )
    else:
        # Default to first item if single item prescription
        target_item = db.query(PrescriptionItem).filter(PrescriptionItem.prescription_id == prescription.id).first()

    if not target_item:
        return VerificationAgentResult(
            valid=False,
            prescription_id=prescription.id,
            prescription_code=prescription.prescription_code,
            prescription_status=prescription.status,
            expiry_valid=True,
            doctor_verified=True,
            patient_verified=True,
            medicine_match=False,
            rejection_reason="Requested medicine does not match any authorized item on this prescription.",
            timestamp=now
        ), prescription, None

    return VerificationAgentResult(
        valid=True,
        prescription_id=prescription.id,
        prescription_code=prescription.prescription_code,
        prescription_status=prescription.status,
        expiry_valid=True,
        doctor_verified=True,
        patient_verified=True,
        medicine_match=True,
        rejection_reason=None,
        timestamp=now
    ), prescription, target_item
