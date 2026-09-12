import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database.base import Base
from app.database.seed_data import seed_database
from app.models.prescription import Prescription
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


def test_integrity_normal_allowance(db_session):
    # Rx 1 has 30 authorized and 0 dispensed
    rx1 = db_session.query(Prescription).filter(Prescription.prescription_code == "RX-2026-DEMO1").first()
    item = rx1.items[0]
    
    result = run_dispensing_integrity_agent(db_session, item, requested_quantity=10)
    assert result.allowed is True
    assert result.authorized_quantity == 30
    assert result.dispensed_quantity == 0
    assert result.remaining_quantity == 30
    assert result.max_permissible_quantity == 10


def test_integrity_excess_rejection(db_session):
    # Rx 2 has 40 authorized and 30 already dispensed (remaining = 10)
    rx2 = db_session.query(Prescription).filter(Prescription.prescription_code == "RX-2026-DEMO2").first()
    item = rx2.items[0]

    # Requesting 20 when only 10 remain
    result = run_dispensing_integrity_agent(db_session, item, requested_quantity=20)
    assert result.allowed is False
    assert result.authorized_quantity == 40
    assert result.dispensed_quantity == 30
    assert result.remaining_quantity == 10
    assert result.max_permissible_quantity == 10
    assert result.is_partial_possible is True
