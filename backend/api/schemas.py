"""
NEXORAS — Module 15: Pydantic Schemas
=====================================
Data validation schemas for FastAPI endpoints.
"""

from pydantic import BaseModel, ConfigDict
from typing import List, Optional, Dict, Any

class HealthResponse(BaseModel):
    status: str
    db_connected: bool

class DashboardSummary(BaseModel):
    total_projects: int
    total_value: float
    high_risk_projects: int
    medium_risk_projects: int
    low_risk_projects: int
    anomaly_count: int
    nlp_alerts: Optional[int] = 0

class ProjectRiskScoreSchema(BaseModel):
    unified_score: float
    risk_tier: str
    tabular_pts: float
    network_pts: float
    graph_pts: float
    financial_pts: float
    nlp_pts: float
    why_flagged_report: Optional[str]
    
    model_config = ConfigDict(from_attributes=True)

class ProjectBase(BaseModel):
    id: str
    mp_id: str
    agency_id: Optional[str]
    work_name: str
    work_category: Optional[str]
    location: Optional[str]
    status: Optional[str]
    sanctioned_amount: float
    final_amount: float

class ProjectResponse(ProjectBase):
    risk_score: Optional[ProjectRiskScoreSchema]
    
    model_config = ConfigDict(from_attributes=True)

class VendorRiskProfileSchema(BaseModel):
    risk_score: Optional[float]
    risk_tier: Optional[str]
    flags: Optional[str]
    
    model_config = ConfigDict(from_attributes=True)

class VendorResponse(BaseModel):
    id: str
    name: str
    total_payout: float
    transaction_count: int
    mp_count: int
    risk_profile: Optional[VendorRiskProfileSchema]
    
    model_config = ConfigDict(from_attributes=True)
        
class PaginatedProjects(BaseModel):
    total: int
    page: int
    size: int
    items: List[ProjectResponse]
    
class PaginatedVendors(BaseModel):
    total: int
    page: int
    size: int
    items: List[VendorResponse]

