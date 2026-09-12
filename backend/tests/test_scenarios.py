import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database.session import SessionLocal, init_db
from app.database.seed_data import seed_database

client = TestClient(app)


@pytest.fixture(scope="module", autouse=True)
def setup_db():
    init_db()
    db = SessionLocal()
    seed_database(db)
    db.close()


def test_scenario_1_normal_purchase():
    # Scenario 1: Normal purchase (10 tabs of Rx 1)
    response = client.post("/api/v1/demo/scenarios/scenario-1/execute")
    assert response.status_code == 200
    data = response.json()
    assert data["decision"] == "APPROVED"
    assert data["approved_quantity"] == 10
    assert data["risk_level"] == "LOW"
    assert data["risk_score"] == 0
    assert len(data["timeline"]) >= 5


def test_scenario_2_partial_cross_pharmacy():
    # Scenario 2: Refill at different pharmacy
    response = client.post("/api/v1/demo/scenarios/scenario-2/execute")
    assert response.status_code == 200
    data = response.json()
    assert data["decision"] == "APPROVED"
    assert data["approved_quantity"] == 10
    assert data["risk_level"] == "LOW"


def test_scenario_3_over_quantity_denial():
    # Scenario 3: Request exceeds remaining
    response = client.post("/api/v1/demo/scenarios/scenario-3/execute")
    assert response.status_code == 200
    data = response.json()
    assert data["decision"] == "REJECTED"
    assert data["approved_quantity"] == 0
    assert data["integrity"]["allowed"] is False
    assert data["remaining_before"] == 10


def test_scenario_4_rapid_multi_provider_hold():
    # Scenario 4: Rapid multi-provider burst
    response = client.post("/api/v1/demo/scenarios/scenario-4/execute")
    assert response.status_code == 200
    data = response.json()
    assert data["decision"] == "ON_HOLD"
    assert data["risk_score"] >= 50
    assert data["requires_pharmacist_review"] is True
    assert data["pattern"]["rapid_provider_switching_detected"] is True
