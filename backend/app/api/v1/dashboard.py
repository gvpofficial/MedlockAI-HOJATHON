from typing import Dict, Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database.session import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.models.prescription import Prescription, PrescriptionItem
from app.models.dispensing import DispensingTransaction
from app.models.risk import Warning, RiskEvent
from app.models.review import ReviewCase
from app.models.pharmacy import Pharmacy
from app.models.doctor import Doctor
from app.models.patient import Patient

router = APIRouter(prefix="/dashboard", tags=["Dashboards"])


@router.get("/patient")
def get_patient_dashboard_data(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    if user.role != "PATIENT" or not user.patient_profile:
        raise HTTPException(status_code=400, detail="User is not a patient.")

    patient_id = user.patient_profile.id
    prescriptions = (
        db.query(Prescription)
        .filter(Prescription.patient_id == patient_id)
        .order_by(Prescription.created_at.desc())
        .all()
    )

    rx_summary = []
    total_active = 0
    for rx in prescriptions:
        if rx.status == "ACTIVE":
            total_active += 1
        items_data = []
        for item in rx.items:
            dispensed = (
                db.query(func.coalesce(func.sum(DispensingTransaction.approved_quantity), 0))
                .filter(
                    DispensingTransaction.prescription_item_id == item.id,
                    DispensingTransaction.status.in_(["APPROVED", "PARTIALLY_APPROVED"])
                )
                .scalar()
            ) or 0
            items_data.append({
                "medicine_name": item.medicine_name,
                "authorized_quantity": item.authorized_quantity,
                "dispensed_quantity": int(dispensed),
                "remaining_quantity": max(0, item.authorized_quantity - int(dispensed)),
                "dosage_instructions": item.dosage_instructions
            })

        rx_summary.append({
            "id": rx.id,
            "prescription_code": rx.prescription_code,
            "doctor_name": rx.doctor.user.full_name if rx.doctor and rx.doctor.user else "Physician",
            "hospital": rx.doctor.hospital_clinic_name if rx.doctor else "",
            "status": rx.status,
            "issue_date": rx.issue_date,
            "expiry_date": rx.expiry_date,
            "qr_code_data": rx.qr_code_data,
            "items": items_data
        })

    # Warnings
    warnings = (
        db.query(Warning)
        .filter(Warning.patient_id == patient_id)
        .order_by(Warning.created_at.desc())
        .limit(10)
        .all()
    )

    # Transactions
    transactions = (
        db.query(DispensingTransaction)
        .join(Prescription)
        .filter(Prescription.patient_id == patient_id)
        .order_by(DispensingTransaction.transaction_timestamp.desc())
        .limit(10)
        .all()
    )
    tx_data = [{
        "id": tx.id,
        "pharmacy_name": tx.pharmacy.pharmacy_name if tx.pharmacy else "Pharmacy",
        "medicine_name": tx.prescription_item.medicine_name if tx.prescription_item else "Medicine",
        "requested_quantity": tx.requested_quantity,
        "approved_quantity": tx.approved_quantity,
        "status": tx.status,
        "timestamp": tx.transaction_timestamp
    } for tx in transactions]

    return {
        "user_name": user.full_name,
        "total_prescriptions": len(prescriptions),
        "active_prescriptions": total_active,
        "prescriptions": rx_summary,
        "warnings": [{
            "id": w.id,
            "severity": w.severity,
            "title": w.title,
            "message": w.message,
            "created_at": w.created_at
        } for w in warnings],
        "recent_transactions": tx_data
    }


@router.get("/doctor")
def get_doctor_dashboard_data(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    doctor_id = None
    doc_name = user.full_name
    doc_lic = "MD-NY-84920"
    doc_hosp = "Metropolitan General Hospital"

    if user.role == "DOCTOR" and user.doctor_profile:
        doctor_id = user.doctor_profile.id
        doc_lic = user.doctor_profile.license_number
        doc_hosp = user.doctor_profile.hospital_clinic_name
    else:
        # Graceful fallback to primary doctor for demo presentation
        first_doc = db.query(Doctor).first()
        if first_doc:
            doctor_id = first_doc.id
            doc_name = first_doc.user.full_name if first_doc.user else "Dr. Arthur Vance, MD"
            doc_lic = first_doc.license_number
            doc_hosp = first_doc.hospital_clinic_name
        else:
            raise HTTPException(status_code=400, detail="User is not a doctor.")

    prescriptions = (
        db.query(Prescription)
        .filter(Prescription.doctor_id == doctor_id)
        .order_by(Prescription.created_at.desc())
        .all()
    )

    # Patients list for dropdown
    patients = db.query(Patient).all()
    patients_dropdown = [{
        "id": p.id,
        "name": p.user.full_name if p.user else "Patient",
        "email": p.user.email if p.user else "",
        "dob": str(p.date_of_birth) if p.date_of_birth else "N/A"
    } for p in patients]

    rx_list = []
    for rx in prescriptions:
        items = [{
            "medicine_name": i.medicine_name,
            "authorized_quantity": i.authorized_quantity,
            "dosage_instructions": i.dosage_instructions
        } for i in rx.items]

        rx_list.append({
            "id": rx.id,
            "prescription_code": rx.prescription_code,
            "patient_name": rx.patient.user.full_name if rx.patient and rx.patient.user else "Patient",
            "status": rx.status,
            "issue_date": rx.issue_date,
            "expiry_date": rx.expiry_date,
            "qr_code_data": rx.qr_code_data,
            "items": items
        })

    return {
        "doctor_name": doc_name,
        "license_number": doc_lic,
        "hospital": doc_hosp,
        "total_prescriptions": len(prescriptions),
        "active_prescriptions": sum(1 for p in prescriptions if p.status == "ACTIVE"),
        "prescriptions": rx_list,
        "available_patients": patients_dropdown
    }


@router.get("/pharmacy")
def get_pharmacy_dashboard_data(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    pharmacy_id = user.pharmacy_profile.id if user.pharmacy_profile else None
    pharmacy_name = user.pharmacy_profile.pharmacy_name if user.pharmacy_profile else "Authorized Pharmacy"
    pharmacy_type = user.pharmacy_profile.pharmacy_type if user.pharmacy_profile else "PHYSICAL_CHAIN"

    query = db.query(DispensingTransaction)
    if pharmacy_id:
        query = query.filter(DispensingTransaction.pharmacy_id == pharmacy_id)

    recent_txs = query.order_by(DispensingTransaction.transaction_timestamp.desc()).limit(15).all()

    tx_list = [{
        "id": tx.id,
        "prescription_code": tx.prescription.prescription_code if tx.prescription else "N/A",
        "patient_name": tx.prescription.patient.user.full_name if tx.prescription and tx.prescription.patient and tx.prescription.patient.user else "Patient",
        "medicine_name": tx.prescription_item.medicine_name if tx.prescription_item else "Medicine",
        "requested_quantity": tx.requested_quantity,
        "approved_quantity": tx.approved_quantity,
        "remaining_after": tx.remaining_after,
        "status": tx.status,
        "rejection_reason": tx.rejection_reason,
        "timestamp": tx.transaction_timestamp
    } for tx in recent_txs]

    # Available pharmacies for cross-testing
    all_pharmacies = db.query(Pharmacy).all()
    pharm_list = [{
        "id": p.id,
        "name": p.pharmacy_name,
        "type": p.pharmacy_type,
        "address": p.address
    } for p in all_pharmacies]

    return {
        "pharmacy_name": pharmacy_name,
        "pharmacy_type": pharmacy_type,
        "total_dispensed_today": sum(t.approved_quantity for t in recent_txs if t.status == "APPROVED"),
        "recent_transactions": tx_list,
        "all_pharmacies": pharm_list
    }
