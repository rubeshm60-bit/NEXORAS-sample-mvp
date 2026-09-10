"""
NEXORAS — Module 15 Test Suite: FastAPI Backend
===============================================
Verifies REST endpoints and data schemas.
"""

import os
import sys
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.db.database import Base, get_db
from backend.db.models import MP, Project, ProjectRiskScore, Vendor
from backend.api.main import app

from sqlalchemy.pool import StaticPool

# Setup test DB
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

def setup_module(module):
    """Populate test DB with dummy data."""
    db = TestingSessionLocal()
    mp1 = MP(id="MP_TEST", mp_name="Test MP", state="Test State", constituency="Test Const")
    vendor1 = Vendor(id="V_TEST", name="Test Vendor")
    p1 = Project(id="PRJ_1", work_name="Work 1", mp_id="MP_TEST", sanctioned_amount=100)
    p2 = Project(id="PRJ_2", work_name="Work 2", mp_id="MP_TEST", sanctioned_amount=200)
    
    r1 = ProjectRiskScore(project_id="PRJ_1", unified_score=90, risk_tier="CRITICAL_RISK", why_flagged_report="Test")
    r2 = ProjectRiskScore(project_id="PRJ_2", unified_score=10, risk_tier="LOW_RISK")
    
    db.add_all([mp1, vendor1, p1, p2, r1, r2])
    db.commit()
    db.close()

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert response.json()["db_connected"] == True

def test_dashboard_summary():
    response = client.get("/dashboard/summary")
    assert response.status_code == 200
    data = response.json()
    assert data["total_projects"] == 2
    assert data["total_value"] == 300.0
    assert data["high_risk_projects"] == 1
    assert data["low_risk_projects"] == 1

def test_get_projects():
    response = client.get("/projects")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 2
    assert len(data["items"]) == 2

def test_get_project_by_id():
    response = client.get("/projects/PRJ_1")
    assert response.status_code == 200
    data = response.json()
    assert data["work_name"] == "Work 1"
    assert data["risk_score"]["risk_tier"] == "CRITICAL_RISK"

def test_get_anomalies():
    response = client.get("/anomalies")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["id"] == "PRJ_1"

def test_get_network():
    response = client.get("/network")
    assert response.status_code == 200
    data = response.json()
    assert "nodes" in data
    assert "edges" in data
