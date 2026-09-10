"""
NEXORAS — Module 14: Database Models
====================================
SQLAlchemy ORM definitions mapping to the MVP data schema.
Contains MP, Project, Vendor, Agency, Payment, and Anomaly/Risk entities.
"""

from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, DateTime, Text
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class MP(Base):
    """Member of Parliament."""
    __tablename__ = "mps"

    id = Column(String, primary_key=True)  # MP ID
    mp_name = Column(String, nullable=False)
    state = Column(String)
    constituency = Column(String)
    party = Column(String)
    
    # Aggregated Stats
    allocated_amount = Column(Float, default=0.0)
    expenditure_amount = Column(Float, default=0.0)
    utilization_rate = Column(Float, default=0.0)
    completion_rate = Column(Float, default=0.0)
    
    # Relationships
    projects = relationship("Project", back_populates="mp")
    risk_score = relationship("MPRiskScore", back_populates="mp", uselist=False)

class Vendor(Base):
    """Contractor or Vendor."""
    __tablename__ = "vendors"

    id = Column(String, primary_key=True)  # Using hash or raw string name if normalized
    name = Column(String, nullable=False)
    
    total_payout = Column(Float, default=0.0)
    transaction_count = Column(Integer, default=0)
    mp_count = Column(Integer, default=0)
    
    # Relationships
    payments = relationship("Payment", back_populates="vendor")
    risk_profile = relationship("VendorRiskProfile", back_populates="vendor", uselist=False)

class Agency(Base):
    """Implementing District Authority (IDA)."""
    __tablename__ = "agencies"
    
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    state = Column(String)
    
    # Relationships
    projects = relationship("Project", back_populates="agency")
    payments = relationship("Payment", back_populates="agency")

class Project(Base):
    """MPLADS Work / Project."""
    __tablename__ = "projects"

    id = Column(String, primary_key=True)  # Work ID
    mp_id = Column(String, ForeignKey("mps.id"))
    agency_id = Column(String, ForeignKey("agencies.id"), nullable=True)
    
    work_name = Column(Text, nullable=False)
    work_category = Column(String)
    location = Column(String)
    status = Column(String)
    
    sanctioned_amount = Column(Float, default=0.0)
    final_amount = Column(Float, default=0.0)
    
    # Relationships
    mp = relationship("MP", back_populates="projects")
    agency = relationship("Agency", back_populates="projects")
    payments = relationship("Payment", back_populates="project")
    risk_score = relationship("ProjectRiskScore", back_populates="project", uselist=False)

class Payment(Base):
    """Disbursement / Expenditure transaction."""
    __tablename__ = "payments"
    
    id = Column(String, primary_key=True)  # Txn ID or surrogate
    project_id = Column(String, ForeignKey("projects.id"))
    vendor_id = Column(String, ForeignKey("vendors.id"))
    agency_id = Column(String, ForeignKey("agencies.id"))
    
    amount = Column(Float, nullable=False)
    date = Column(DateTime, nullable=True)
    status = Column(String)
    
    # Relationships
    project = relationship("Project", back_populates="payments")
    vendor = relationship("Vendor", back_populates="payments")
    agency = relationship("Agency", back_populates="payments")

class ProjectRiskScore(Base):
    """Unified Risk Score and Explainability for a Project."""
    __tablename__ = "project_risk_scores"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(String, ForeignKey("projects.id"), unique=True)
    
    unified_score = Column(Float, nullable=False)
    risk_tier = Column(String, nullable=False)  # CRITICAL_RISK, HIGH_RISK, etc.
    
    # Pillar sub-scores (0-100 pts)
    tabular_pts = Column(Float, default=0.0)
    network_pts = Column(Float, default=0.0)
    graph_pts = Column(Float, default=0.0)
    financial_pts = Column(Float, default=0.0)
    nlp_pts = Column(Float, default=0.0)
    
    # Module 13 Explanation String
    why_flagged_report = Column(Text)
    
    # Relationships
    project = relationship("Project", back_populates="risk_score")

class MPRiskScore(Base):
    """Aggregated risk signals at the MP level."""
    __tablename__ = "mp_risk_scores"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    mp_id = Column(String, ForeignKey("mps.id"), unique=True)
    
    anomaly_score = Column(Float)
    is_anomalous = Column(Boolean, default=False)
    why_flagged_report = Column(Text)
    
    # Relationships
    mp = relationship("MP", back_populates="risk_score")

class VendorRiskProfile(Base):
    """Risk signals at the Vendor level (Monopoly, Syndicate)."""
    __tablename__ = "vendor_risk_profiles"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    vendor_id = Column(String, ForeignKey("vendors.id"), unique=True)
    
    risk_score = Column(Float)
    risk_tier = Column(String)
    flags = Column(String)  # Comma-separated list of flags (e.g. MULTI_MP_SYNDICATE)
    
    # Relationships
    vendor = relationship("Vendor", back_populates="risk_profile")
