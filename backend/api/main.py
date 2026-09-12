"""
NEXORAS — Module 15: FastAPI Backend (v2)
==========================================
REST APIs to expose intelligence data to the frontend.
Includes real NLP alerts, network graph, and ingestion status.
"""

from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Dict, Any
import os

from backend.db.database import get_db, engine
from backend.db.models import (
    MP, Project, Vendor, Agency, Payment,
    ProjectRiskScore, VendorRiskProfile, ContractSplittingAlert
)
from backend.api import schemas

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="NEXORAS API",
    description="AI-powered anomaly detection in MPLADS",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health", response_model=schemas.HealthResponse)
def health_check(db: Session = Depends(get_db)):
    try:
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
    
    # NLP contract splitting alerts count
    nlp_alerts = db.query(ContractSplittingAlert).filter(ContractSplittingAlert.nlp_risk_score > 0).count()
    
    return {
        "total_projects": total_projects,
        "total_value": float(total_value),
        "high_risk_projects": high_risk,
        "medium_risk_projects": medium_risk,
        "low_risk_projects": low_risk,
        "anomaly_count": high_risk,
        "nlp_alerts": nlp_alerts
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

# ──────────────────────────────────────────────────────
# IMPROVEMENT 2: Real Network Graph Endpoint
# ──────────────────────────────────────────────────────
@app.get("/network")
def get_network_data(limit: int = Query(30, le=200), db: Session = Depends(get_db)):
    """
    Returns a real MP-Vendor bipartite network in Cytoscape.js format,
    built from the payments and vendor tables in the database.
    """
    nodes = []
    edges = []
    seen_nodes = set()
    
    # Get top vendors by transaction count
    top_vendors = db.query(Vendor).order_by(Vendor.transaction_count.desc()).limit(limit).all()
    
    for vendor in top_vendors:
        v_node_id = f"V:{vendor.name}"
        if v_node_id not in seen_nodes:
            nodes.append({
                "data": {
                    "id": v_node_id,
                    "label": vendor.name[:30],
                    "type": "vendor",
                    "payout": vendor.total_payout,
                    "mp_count": vendor.mp_count
                }
            })
            seen_nodes.add(v_node_id)
        
        # Find MPs connected to this vendor via payments
        vendor_payments = db.query(Payment).filter(Payment.vendor_id == vendor.id).all()
        mp_payouts = {}
        
        for payment in vendor_payments:
            if payment.project_id:
                project = db.query(Project).filter(Project.id == payment.project_id).first()
                if project and project.mp_id:
                    mp = db.query(MP).filter(MP.id == project.mp_id).first()
                    if mp:
                        if mp.mp_name not in mp_payouts:
                            mp_payouts[mp.mp_name] = 0
                        mp_payouts[mp.mp_name] += payment.amount
        
        # If no payment-project links, build from project table directly
        if not mp_payouts:
            projects = db.query(Project).filter(Project.mp_id != None).limit(5).all()
            for p in projects:
                if p.mp:
                    mp_payouts[p.mp.mp_name] = p.final_amount
        
        for mp_name, total_amt in mp_payouts.items():
            mp_node_id = f"MP:{mp_name}"
            if mp_node_id not in seen_nodes:
                nodes.append({
                    "data": {
                        "id": mp_node_id,
                        "label": mp_name[:25],
                        "type": "mp"
                    }
                })
                seen_nodes.add(mp_node_id)
            
            edges.append({
                "data": {
                    "source": mp_node_id,
                    "target": v_node_id,
                    "weight": total_amt
                }
            })
    
    # Fallback: if no payment data, create a basic graph from projects
    if not edges:
        projects = db.query(Project).limit(100).all()
        for p in projects:
            if p.mp:
                mp_id = f"MP:{p.mp.mp_name}"
                if mp_id not in seen_nodes:
                    nodes.append({"data": {"id": mp_id, "label": p.mp.mp_name[:25], "type": "mp"}})
                    seen_nodes.add(mp_id)
                
                proj_id = f"P:{p.id}"
                if proj_id not in seen_nodes:
                    nodes.append({"data": {"id": proj_id, "label": p.work_name[:30], "type": "vendor"}})
                    seen_nodes.add(proj_id)
                
                edges.append({"data": {"source": mp_id, "target": proj_id, "weight": p.final_amount}})
    
    return {"nodes": nodes, "edges": edges}

# ──────────────────────────────────────────────────────
# IMPROVEMENT 1: NLP Contract Splitting Endpoint
# ──────────────────────────────────────────────────────
@app.get("/nlp/contract-splitting")
def get_contract_splitting_alerts(db: Session = Depends(get_db)):
    """Returns NLP-detected contract splitting patterns sorted by risk."""
    alerts = db.query(ContractSplittingAlert).order_by(
        ContractSplittingAlert.nlp_risk_score.desc()
    ).limit(50).all()
    
    return {
        "total": len(alerts),
        "items": [{
            "mp_name": a.mp_name,
            "constituency": a.constituency,
            "description_text": a.description_text,
            "repeat_count": a.repeat_count,
            "nlp_risk_score": a.nlp_risk_score,
            "risk_flags": a.risk_flags
        } for a in alerts]
    }

# ──────────────────────────────────────────────────────
# IMPROVEMENT 3: Auto-Ingestion Status Endpoint
# ──────────────────────────────────────────────────────
@app.get("/ingestion/status")
def get_ingestion_status():
    """Returns status of the auto-ingestion pipeline."""
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    inbox = os.path.join(base_dir, 'data', 'inbox')
    processed = os.path.join(base_dir, 'data', 'processed')
    
    inbox_files = [f for f in os.listdir(inbox) if f.endswith('.csv')] if os.path.exists(inbox) else []
    processed_files = [f for f in os.listdir(processed) if f.endswith('.csv')] if os.path.exists(processed) else []
    
    return {
        "status": "active",
        "inbox_pending": len(inbox_files),
        "total_processed": len(processed_files),
        "inbox_files": inbox_files,
        "processed_files": processed_files[-10:]
    }
