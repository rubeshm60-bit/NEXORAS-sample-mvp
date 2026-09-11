"""
NEXORAS — Module 15: FastAPI Backend
====================================
REST APIs to expose intelligence data to the frontend.
"""

from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Dict, Any

from backend.db.database import get_db, engine
from backend.db.models import MP, Project, Vendor, Agency, ProjectRiskScore, VendorRiskProfile
from backend.api import schemas

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="NEXORAS API",
    description="AI-powered anomaly detection in MPLADS",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for the MVP
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health", response_model=schemas.HealthResponse)
def health_check(db: Session = Depends(get_db)):
    try:
        # Simple query to ensure DB is connected
        db.query(MP).first()
        db_connected = True
    except Exception:
        db_connected = False
        
    return {"status": "ok", "db_connected": db_connected}

@app.get("/dashboard/summary", response_model=schemas.DashboardSummary)
def get_dashboard_summary(db: Session = Depends(get_db)):
    total_projects = db.query(Project).count()
    total_value = db.query(func.sum(Project.sanctioned_amount)).scalar() or 0.0
    
    high_risk = db.query(ProjectRiskScore).filter(ProjectRiskScore.risk_tier.in_(["CRITICAL_RISK", "HIGH_RISK"])).count()
    medium_risk = db.query(ProjectRiskScore).filter(ProjectRiskScore.risk_tier == "MEDIUM_RISK").count()
    low_risk = db.query(ProjectRiskScore).filter(ProjectRiskScore.risk_tier == "LOW_RISK").count()
    
    return {
        "total_projects": total_projects,
        "total_value": float(total_value),
        "high_risk_projects": high_risk,
        "medium_risk_projects": medium_risk,
        "low_risk_projects": low_risk,
        "anomaly_count": high_risk  # Simplifying anomaly count as high risk count for MVP
    }

@app.get("/projects", response_model=schemas.PaginatedProjects)
def get_projects(
    skip: int = Query(0, ge=0), 
    limit: int = Query(50, le=100),
    risk_tier: str = None,
    db: Session = Depends(get_db)
):
    query = db.query(Project)
    
    if risk_tier:
        query = query.join(Project.risk_score).filter(ProjectRiskScore.risk_tier == risk_tier)
        
    total = query.count()
    projects = query.offset(skip).limit(limit).all()
    
    return {
        "total": total,
        "page": skip // limit + 1 if limit > 0 else 1,
        "size": limit,
        "items": projects
    }

@app.get("/projects/{project_id}", response_model=schemas.ProjectResponse)
def get_project(project_id: str, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project

@app.get("/anomalies", response_model=schemas.PaginatedProjects)
def get_anomalies(skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    # Fetch projects that are high or critical risk
    query = db.query(Project).join(Project.risk_score).filter(
        ProjectRiskScore.risk_tier.in_(["CRITICAL_RISK", "HIGH_RISK"])
    ).order_by(ProjectRiskScore.unified_score.desc())
    
    total = query.count()
    projects = query.offset(skip).limit(limit).all()
    
    return {
        "total": total,
        "page": skip // limit + 1 if limit > 0 else 1,
        "size": limit,
        "items": projects
    }

@app.get("/vendors", response_model=schemas.PaginatedVendors)
def get_vendors(skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    query = db.query(Vendor)
    total = query.count()
    vendors = query.offset(skip).limit(limit).all()
    
    return {
        "total": total,
        "page": skip // limit + 1 if limit > 0 else 1,
        "size": limit,
        "items": vendors
    }

@app.get("/vendors/{vendor_id}", response_model=schemas.VendorResponse)
def get_vendor(vendor_id: str, db: Session = Depends(get_db)):
    vendor = db.query(Vendor).filter(Vendor.id == vendor_id).first()
    if not vendor:
        raise HTTPException(status_code=404, detail="Vendor not found")
    return vendor

@app.get("/network")
def get_network_data(db: Session = Depends(get_db)):
    """
    Returns a small subgraph in Cytoscape.js format.
    For the MVP, we mock this endpoint or return a simplified JSON structure 
    to prevent overwhelming the browser with 30k nodes.
    """
    # Just a mock structure for the frontend Module 16
    return {
        "nodes": [
            {"data": {"id": "MP_1", "label": "MP John", "type": "mp"}},
            {"data": {"id": "V_1", "label": "Acme Corp", "type": "vendor"}}
        ],
        "edges": [
            {"data": {"source": "MP_1", "target": "V_1", "weight": 50000}}
        ]
    }
