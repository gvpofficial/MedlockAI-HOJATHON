import hashlib
import json
import uuid
from datetime import datetime, timezone
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.api.deps import get_current_user, RoleChecker
from app.core.audit import log_audit_event
from app.agents.orchestrator import run_medlock_agent_orchestrator
from app.models.user import User
from app.models.pharmacy import Pharmacy
from app.models.prescription import Prescription, PrescriptionItem
from app.models.dispensing import DispensingTransaction, PurchaseAttempt
from app.models.risk import RiskEvent, Warning
from app.models.review import ReviewCase
from app.schemas.agent import MultiAgentEvaluationResult
from app.schemas.dispensing import (
    DispenseVerifyRequest,
    DispenseEvaluateRequest,
    DispenseExecuteRequest,
    DispenseExecuteResponse,
    DispensingTransactionResponse
)

router = APIRouter(prefix="/dispense", tags=["Dispensing"])


def _resolve_pharmacy_id(user: User, db: Session, pharmacy_id_override: Optional[str] = None) -> str:
    if user.role == "PHARMACY" and user.pharmacy_profile:
        return user.pharmacy_profile.id
    if pharmacy_id_override:
        p = db.query(Pharmacy).filter(Pharmacy.id == pharmacy_id_override).first()
        if p:
            return p.id
    # Fallback to first pharmacy in database
    p_first = db.query(Pharmacy).first()
    if p_first:
        return p_first.id
    raise HTTPException(status_code=400, detail="No active pharmacy found to associate with this transaction.")


@router.post("/evaluate", response_model=MultiAgentEvaluationResult)
def evaluate_dispensing_request(
    req: DispenseEvaluateRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    pharmacy_id = _resolve_pharmacy_id(user, db, req.pharmacy_id)
    
    clean_code = req.prescription_code.strip()
    if clean_code.startswith("MEDLOCK_RX:"):
        parts = clean_code.split(":")
        if len(parts) >= 2:
            clean_code = parts[1]

    result, _, _ = run_medlock_agent_orchestrator(
        db=db,
        prescription_code=clean_code,
        requested_quantity=req.requested_quantity,
        pharmacy_id=pharmacy_id,
        medicine_name=req.medicine_name,
        prescription_item_id=req.prescription_item_id
    )

    return result


@router.post("/execute", response_model=DispenseExecuteResponse)
def execute_dispensing_request(
    req: DispenseExecuteRequest,
    db: Session = Depends(get_db),
    user: User = Depends(RoleChecker(["PHARMACY", "ADMIN"]))
):
    pharmacy_id = _resolve_pharmacy_id(user, db, req.pharmacy_id)
    pharmacy = db.query(Pharmacy).filter(Pharmacy.id == pharmacy_id).first()

    clean_code = req.prescription_code.strip()
    if clean_code.startswith("MEDLOCK_RX:"):
        parts = clean_code.split(":")
        if len(parts) >= 2:
            clean_code = parts[1]

    # Run agent orchestrator
    eval_result, prescription, item = run_medlock_agent_orchestrator(
        db=db,
        prescription_code=clean_code,
        requested_quantity=req.requested_quantity,
        pharmacy_id=pharmacy_id,
        medicine_name=req.medicine_name,
        prescription_item_id=req.prescription_item_id
    )

    if not prescription or not item:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=eval_result.verification.rejection_reason or "Invalid prescription or item."
        )

    now = datetime.now(timezone.utc)
    decision = eval_result.decision
    approved_qty = eval_result.approved_quantity
    rem_before = eval_result.remaining_before
    rem_after = eval_result.remaining_after

    # Compute transaction integrity hash
    tx_hash_input = f"{prescription.id}|{item.id}|{pharmacy_id}|{req.requested_quantity}|{approved_qty}|{decision}|{now.isoformat()}"
    tx_hash = hashlib.sha256(tx_hash_input.encode()).hexdigest()

    # 1. Create Dispensing Transaction Record
    tx = DispensingTransaction(
        prescription_id=prescription.id,
        prescription_item_id=item.id,
        pharmacy_id=pharmacy_id,
        requested_quantity=req.requested_quantity,
        approved_quantity=approved_qty,
        remaining_before=rem_before,
        remaining_after=rem_after,
        status=decision,
        rejection_reason=eval_result.integrity.reason if decision == "REJECTED" else None,
        transaction_timestamp=now,
        integrity_hash=tx_hash
    )
    db.add(tx)
    db.flush()

    # 2. Record Purchase Attempt for Pattern Velocity Tracking
    attempt = PurchaseAttempt(
        prescription_id=prescription.id,
        pharmacy_id=pharmacy_id,
        requested_quantity=req.requested_quantity,
        attempt_timestamp=now,
        outcome=decision
    )
    db.add(attempt)

    # 3. Handle Risk Event and Review Case if High Risk or On Hold
    review_case_id = None
    if eval_result.risk_score > 0 or decision in ["ON_HOLD", "REJECTED"]:
        risk_event = RiskEvent(
            transaction_id=tx.id,
            prescription_id=prescription.id,
            patient_id=prescription.patient_id,
            risk_score=eval_result.risk_score,
            risk_level=eval_result.risk_level,
            factors_json=[f.dict() for f in eval_result.risk.risk_factors],
            agent_summary=eval_result.summary.clinical_summary
        )
        db.add(risk_event)
        db.flush()

        if decision == "ON_HOLD" or eval_result.requires_pharmacist_review:
            case_num = f"CASE-{datetime.now().year}-{str(uuid.uuid4())[:6].upper()}"
            review_case = ReviewCase(
                case_number=case_num,
                risk_event_id=risk_event.id,
                prescription_id=prescription.id,
                patient_id=prescription.patient_id,
                status="PENDING",
                ai_summary=eval_result.summary.clinical_summary,
                reviewer_notes=f"Automated hold triggered by MedLock AI Agent System. Risk Score: {eval_result.risk_score} ({eval_result.risk_level})."
            )
            db.add(review_case)
            db.flush()
            review_case_id = review_case.id

            # Create Patient Warning
            warning = Warning(
                patient_id=prescription.patient_id,
                prescription_id=prescription.id,
                severity="CRITICAL" if eval_result.risk_level == "CRITICAL" else "WARNING",
                title=f"Dispensing Safety Hold ({pharmacy.pharmacy_name if pharmacy else 'Pharmacy'})",
                message=f"A dispensing request for {item.medicine_name} was placed on hold for clinical verification. Case ref: {case_num}."
            )
            db.add(warning)

    elif decision == "REJECTED":
        # Create Patient Warning for rejected over-quantity attempt
        warning = Warning(
            patient_id=prescription.patient_id,
            prescription_id=prescription.id,
            severity="WARNING",
            title="Prescription Quantity Limit Exceeded",
            message=f"Attempted to dispense {req.requested_quantity} units of {item.medicine_name}, but only {rem_before} units were remaining."
        )
        db.add(warning)

    # 4. Check if prescription is now fully exhausted
    if decision == "APPROVED" and rem_after == 0:
        # Check if all items in prescription are exhausted
        all_items = db.query(PrescriptionItem).filter(PrescriptionItem.prescription_id == prescription.id).all()
        # Update current item remaining
        item.remaining_quantity = 0
        db.commit()
    else:
        db.commit()

    # 5. Cryptographic Audit Log
    log_audit_event(
        db=db,
        event_type=f"DISPENSING_{decision}",
        target_entity="dispensing_transactions",
        target_id=tx.id,
        actor_user_id=user.id,
        actor_role=user.role,
        details={
            "prescription_code": prescription.prescription_code,
            "medicine_name": item.medicine_name,
            "pharmacy_id": pharmacy_id,
            "requested_quantity": req.requested_quantity,
            "approved_quantity": approved_qty,
            "remaining_after": rem_after,
            "decision": decision,
            "risk_score": eval_result.risk_score,
            "tx_hash": tx_hash
        }
    )

    eval_result.review_case_id = review_case_id

    messages = {
        "APPROVED": f"Dispensing approved successfully for {approved_qty} units of {item.medicine_name}.",
        "PARTIALLY_APPROVED": f"Partially approved {approved_qty} units (Requested: {req.requested_quantity}).",
        "REJECTED": f"Dispensing rejected: {eval_result.integrity.reason}",
        "ON_HOLD": f"Dispensing placed ON HOLD for pharmacist review (Risk Score: {eval_result.risk_score}). Case #{review_case_id or ''}"
    }

    return DispenseExecuteResponse(
        transaction_id=tx.id,
        decision=decision,
        message=messages.get(decision, f"Transaction status: {decision}"),
        remaining_quantity=rem_after,
        evaluation=eval_result
    )


@router.get("/history", response_model=List[DispensingTransactionResponse])
def get_dispensing_history(
    prescription_id: Optional[str] = None,
    pharmacy_id: Optional[str] = None,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    query = db.query(DispensingTransaction)
    
    if user.role == "PATIENT" and user.patient_profile:
        # Join prescription to ensure patient only sees their own
        query = query.join(Prescription).filter(Prescription.patient_id == user.patient_profile.id)
    elif user.role == "PHARMACY" and user.pharmacy_profile:
        query = query.filter(DispensingTransaction.pharmacy_id == user.pharmacy_profile.id)
    elif prescription_id:
        query = query.filter(DispensingTransaction.prescription_id == prescription_id)
    elif pharmacy_id:
        query = query.filter(DispensingTransaction.pharmacy_id == pharmacy_id)

    txs = query.order_by(DispensingTransaction.transaction_timestamp.desc()).limit(100).all()

    response = []
    for tx in txs:
        response.append(
            DispensingTransactionResponse(
                id=tx.id,
                prescription_id=tx.prescription_id,
                prescription_code=tx.prescription.prescription_code if tx.prescription else None,
                prescription_item_id=tx.prescription_item_id,
                medicine_name=tx.prescription_item.medicine_name if tx.prescription_item else "Unknown",
                pharmacy_id=tx.pharmacy_id,
                pharmacy_name=tx.pharmacy.pharmacy_name if tx.pharmacy else "Unknown Pharmacy",
                requested_quantity=tx.requested_quantity,
                approved_quantity=tx.approved_quantity,
                remaining_before=tx.remaining_before,
                remaining_after=tx.remaining_after,
                status=tx.status,
                rejection_reason=tx.rejection_reason,
                transaction_timestamp=tx.transaction_timestamp,
                integrity_hash=tx.integrity_hash
            )
        )
    return response
