from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.session import get_db, engine
from app.database.base import Base
from app.database.seed_data import seed_database
from app.models.prescription import Prescription
from app.models.pharmacy import Pharmacy
from app.models.dispensing import DispensingTransaction, PurchaseAttempt
from app.agents.orchestrator import run_medlock_agent_orchestrator
from app.schemas.agent import MultiAgentEvaluationResult

router = APIRouter(prefix="/demo", tags=["Demo & Scenarios"])


@router.post("/reset-seed")
def reset_and_seed_database(db: Session = Depends(get_db)):
    # Drop all and re-create
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    seed_database(db)
    return {
        "status": "success",
        "message": "Database successfully reset and seeded with 5 patients, 2 doctors, 5 pharmacies, and 5 prescriptions."
    }


@router.get("/scenarios")
def get_demo_scenarios():
    return [
        {
            "id": "scenario-1",
            "title": "Scenario 1: Normal Authorized Purchase",
            "description": "Patient Johnathan Doe visits Metro Pharmacy requesting 10 tablets of Demo Restricted Medicine X (Authorized: 30, Previously Dispensed: 0).",
            "expected_outcome": "APPROVED",
            "prescription_code": "RX-2026-DEMO1",
            "requested_quantity": 10,
            "pharmacy_target": "HealthFirst Pharmacy - Metro Branch",
            "risk_level": "LOW (0/100)"
        },
        {
            "id": "scenario-2",
            "title": "Scenario 2: Partial Cross-Pharmacy Refill",
            "description": "Following initial purchase, patient visits a DIFFERENT pharmacy (CarePlus Downtown) requesting 10 tablets. System validates central remaining balance (20 -> 10).",
            "expected_outcome": "APPROVED",
            "prescription_code": "RX-2026-DEMO1",
            "requested_quantity": 10,
            "pharmacy_target": "CarePlus Downtown Pharmacy",
            "risk_level": "LOW (0/100)"
        },
        {
            "id": "scenario-3",
            "title": "Scenario 3: Deterministic Over-Quantity Denial",
            "description": "Sarah Jenkins requests 20 tablets of Oxycodone at CVS Union Square. Remaining authorized balance is only 10 tablets. Central deterministic integrity blocks excess dispensing.",
            "expected_outcome": "REJECTED",
            "prescription_code": "RX-2026-DEMO2",
            "requested_quantity": 20,
            "pharmacy_target": "CVS Pharmacy Union Square",
            "risk_level": "CRITICAL / REJECTED"
        },
        {
            "id": "scenario-4",
            "title": "Scenario 4: Rapid Multi-Provider Anomaly Hold",
            "description": "David Miller attempts purchase at 4th provider after visiting 3 pharmacies (including online) within 2 hours with prior rejection. AI Agent flags rapid provider switching and places transaction ON HOLD.",
            "expected_outcome": "ON_HOLD / PHARMACIST_REVIEW",
            "prescription_code": "RX-2026-DEMO3",
            "requested_quantity": 15,
            "pharmacy_target": "Walgreens 42nd St",
            "risk_level": "HIGH (85/100)"
        }
    ]


@router.post("/scenarios/{scenario_id}/execute", response_model=MultiAgentEvaluationResult)
def execute_demo_scenario(scenario_id: str, db: Session = Depends(get_db)):
    if scenario_id == "scenario-1":
        # Scenario 1: Normal purchase at Metro Pharmacy
        pharm = db.query(Pharmacy).filter(Pharmacy.pharmacy_name.ilike("%Metro%")).first()
        res, _, _ = run_medlock_agent_orchestrator(
            db=db,
            prescription_code="RX-2026-DEMO1",
            requested_quantity=10,
            pharmacy_id=pharm.id if pharm else ""
        )
        return res

    elif scenario_id == "scenario-2":
        # Scenario 2: Partial refill at CarePlus Downtown
        pharm = db.query(Pharmacy).filter(Pharmacy.pharmacy_name.ilike("%CarePlus%")).first()
        res, _, _ = run_medlock_agent_orchestrator(
            db=db,
            prescription_code="RX-2026-DEMO1",
            requested_quantity=10,
            pharmacy_id=pharm.id if pharm else ""
        )
        return res

    elif scenario_id == "scenario-3":
        # Scenario 3: Over-quantity rejection at CVS
        pharm = db.query(Pharmacy).filter(Pharmacy.pharmacy_name.ilike("%CVS%")).first()
        res, _, _ = run_medlock_agent_orchestrator(
            db=db,
            prescription_code="RX-2026-DEMO2",
            requested_quantity=20,  # Only 10 remaining
            pharmacy_id=pharm.id if pharm else ""
        )
        return res

    elif scenario_id == "scenario-4":
        # Scenario 4: Rapid multi-provider burst
        # Ensure previous burst timestamps are active relative to current execution time
        now = datetime.now(timezone.utc)
        rx3 = db.query(Prescription).filter(Prescription.prescription_code == "RX-2026-DEMO3").first()
        if rx3:
            txs = db.query(DispensingTransaction).filter(DispensingTransaction.prescription_id == rx3.id).all()
            if len(txs) >= 1:
                txs[0].transaction_timestamp = now - timedelta(minutes=45)
            if len(txs) >= 2:
                txs[1].transaction_timestamp = now - timedelta(minutes=25)
            attempts = db.query(PurchaseAttempt).filter(PurchaseAttempt.prescription_id == rx3.id).all()
            for att in attempts:
                att.attempt_timestamp = now - timedelta(minutes=10)
            db.commit()

        pharm = db.query(Pharmacy).filter(Pharmacy.pharmacy_name.ilike("%Walgreens%")).first()
        res, _, _ = run_medlock_agent_orchestrator(
            db=db,
            prescription_code="RX-2026-DEMO3",
            requested_quantity=15,
            pharmacy_id=pharm.id if pharm else ""
        )
        return res

    else:
        raise HTTPException(status_code=404, detail=f"Scenario '{scenario_id}' not found.")
