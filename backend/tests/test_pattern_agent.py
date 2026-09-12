import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database.base import Base
from app.database.seed_data import seed_database
from app.models.prescription import Prescription
from app.models.pharmacy import Pharmacy
from app.agents.agent_pattern import run_cross_pharmacy_pattern_agent
from app.agents.agent_risk_engine import run_risk_assessment_engine
from app.agents.agent_integrity import run_dispensing_integrity_agent


@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    seed_database(session)
    yield session
    session.close()


def test_cross_pharmacy_burst_detection(db_session):
    # Rx 3 has multiple pharmacies accessed within 2h and an online rejection
    rx3 = db_session.query(Prescription).filter(Prescription.prescription_code == "RX-2026-DEMO3").first()
    pharm = db_session.query(Pharmacy).filter(Pharmacy.pharmacy_name.ilike("%Walgreens%")).first()
    
    pattern_res = run_cross_pharmacy_pattern_agent(
        db=db_session,
        prescription_id=rx3.id,
        current_pharmacy_id=pharm.id
    )

    assert pattern_res.anomaly_detected is True
    assert pattern_res.rapid_provider_switching_detected is True
    assert pattern_res.distinct_pharmacies_2h >= 2
    assert pattern_res.burst_after_rejection_detected is True

    # Test Risk Score
    integrity_res = run_dispensing_integrity_agent(db_session, rx3.items[0], requested_quantity=15)
    risk_res = run_risk_assessment_engine(integrity_res, pattern_res)
    assert risk_res.risk_score >= 50
    assert risk_res.risk_level in ["HIGH", "CRITICAL"]
