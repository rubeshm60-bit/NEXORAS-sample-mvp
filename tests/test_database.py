"""
NEXORAS — Module 14 Test Suite: Database
========================================
Verifies SQLAlchemy models, relationships, and session commits.
"""

import os
import sys
import unittest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.db.models import Base, MP, Vendor, Agency, Project, Payment, ProjectRiskScore

class TestDatabaseMVP(unittest.TestCase):
    def setUp(self):
        """Setup an in-memory SQLite database for testing."""
        self.engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(bind=self.engine)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        self.db = self.SessionLocal()

    def tearDown(self):
        self.db.close()
        Base.metadata.drop_all(bind=self.engine)

    def test_01_create_and_query_mp(self):
        """Test MP creation."""
        mp = MP(id="MP001", mp_name="Test MP", state="Test State")
        self.db.add(mp)
        self.db.commit()
        
        result = self.db.query(MP).filter(MP.id == "MP001").first()
        self.assertIsNotNone(result)
        self.assertEqual(result.mp_name, "Test MP")
        self.assertEqual(result.allocated_amount, 0.0)

    def test_02_relationships(self):
        """Test relationships between Project, MP, Agency, and RiskScore."""
        # Setup entities
        mp = MP(id="MP002", mp_name="Jane Doe")
        agency = Agency(id="IDA001", name="Test Agency")
        project = Project(
            id="PRJ001", 
            work_name="Build Road", 
            mp_id="MP002", 
            agency_id="IDA001",
            sanctioned_amount=500000.0
        )
        risk = ProjectRiskScore(
            project_id="PRJ001",
            unified_score=85.5,
            risk_tier="CRITICAL_RISK",
            why_flagged_report="High cost deviation."
        )
        
        self.db.add_all([mp, agency, project, risk])
        self.db.commit()
        
        # Verify relationships
        q_project = self.db.query(Project).filter(Project.id == "PRJ001").first()
        self.assertEqual(q_project.mp.mp_name, "Jane Doe")
        self.assertEqual(q_project.agency.name, "Test Agency")
        self.assertEqual(q_project.risk_score.risk_tier, "CRITICAL_RISK")
        self.assertEqual(q_project.risk_score.unified_score, 85.5)
        
        # Verify reverse relationships
        q_mp = self.db.query(MP).filter(MP.id == "MP002").first()
        self.assertEqual(len(q_mp.projects), 1)
        self.assertEqual(q_mp.projects[0].work_name, "Build Road")

    def test_03_vendor_and_payment(self):
        """Test Vendor to Payment relationships."""
        vendor = Vendor(id="V001", name="ACME Corp")
        project = Project(id="PRJ002", work_name="Test Work")
        payment = Payment(
            id="TXN001",
            project_id="PRJ002",
            vendor_id="V001",
            amount=10000.0
        )
        
        self.db.add_all([vendor, project, payment])
        self.db.commit()
        
        q_vendor = self.db.query(Vendor).filter(Vendor.id == "V001").first()
        self.assertEqual(len(q_vendor.payments), 1)
        self.assertEqual(q_vendor.payments[0].amount, 10000.0)

if __name__ == '__main__':
    unittest.main()
