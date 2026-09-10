"""
NEXORAS — Module 17: E2E Integration Pipeline
=============================================
Runs the full data pipeline from ingestion to database seeding.
"""

import os
import sys
import pandas as pd
import numpy as np

# Adjust path so backend is importable
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from backend.ingestion.loader import load_mp_summary, load_completed_works, load_expenditures, load_recommended_works
from backend.cleaning.cleaner import clean_mp_summary, clean_completed_works, clean_recommended_works, clean_expenditures

from backend.engine.isolation_forest import MPIsolationForest, WorkIsolationForest
from backend.engine.network_graph import MPLADSNetworkGraph
from backend.scoring.risk_engine import UnifiedRiskEngine
from backend.db.database import init_db, SessionLocal, engine
from backend.db.models import Base, MP, Project, Vendor, Agency, ProjectRiskScore, MPRiskScore, VendorRiskProfile
from backend.engine.shap_explainer import ModelExplainer
from backend.engine.why_flagged import WhyFlaggedEngine

import hashlib

def run():
    print("==================================================")
    print(" NEXORAS E2E PIPELINE ")
    print("==================================================")
    
    print("\n[1/7] INITIALIZING DATABASE...")
    # Drop all existing tables and re-create to ensure clean state
    Base.metadata.drop_all(bind=engine)
    init_db()
    
    print("\n[2/7] INGESTING & CLEANING DATA...")
    try:
        mp_df_raw = load_mp_summary()
        cw_df_raw = load_completed_works()
        rw_df_raw = load_recommended_works()
        exp_df_raw = load_expenditures()
        
        mp_df = clean_mp_summary(mp_df_raw)
        cw_df = clean_completed_works(cw_df_raw)
        rw_df = clean_recommended_works(rw_df_raw)
        exp_df = clean_expenditures(exp_df_raw)
        print(f"Loaded {len(mp_df)} MPs, {len(cw_df)} Completed Works, {len(exp_df)} Expenditures.")
    except Exception as e:
        print(f"WARNING: Could not load real datasets ({e}). Falling back to dummy data for MVP pipeline demonstration.")
        # Fallback dummy data
        mp_df = pd.DataFrame({
            'mp_id': ['MP1', 'MP2'],
            'mp_name': ['John Doe', 'Jane Smith'],
            'state': ['DL', 'MH'],
            'constituency': ['C1', 'C2'],
            'party': ['A', 'B'],
            'allocated_amount': [5000000, 5000000],
            'expenditure_amount': [4500000, 2000000],
            'utilization_rate': [90.0, 40.0],
            'completion_rate': [85.0, 30.0]
        })
        
        cw_df = pd.DataFrame({
            'work_id': ['W1', 'W2', 'W3'],
            'mp_id': ['MP1', 'MP1', 'MP2'],
            'work_name': ['Road Construction', 'Water Tank', 'School Building'],
            'work_category': ['Infrastructure', 'Water', 'Education'],
            'status': ['Completed', 'Completed', 'In Progress'],
            'sanctioned_amount': [1000000, 500000, 2000000],
            'final_amount': [1050000, 500000, 1000000]
        })
        
        exp_df = pd.DataFrame({
            'txn_id': ['T1', 'T2', 'T3'],
            'work_id': ['W1', 'W2', 'W3'],
            'vendor_name': ['Acme Construction', 'AquaCorp', 'Acme Construction'],
            'amount': [1050000, 500000, 1000000]
        })
        rw_df = pd.DataFrame()

    print("\n[3/7] BUILDING ML FEATURES...")
    # Mocking Feature Building since actual datasets might be missing or complex
    
    # We will limit the pipeline to the first 500 projects for speed during the hackathon MVP
    cw_df = cw_df.head(500).copy()
    
    # We will generate synthetic feature matrices to simulate the pipeline
    np.random.seed(42)
    # Works feature matrix
    works_features = cw_df[['work_id', 'final_amount']].copy()
    works_features['cost_deviation'] = np.random.randn(len(cw_df))
    works_features['delay_days'] = np.random.randint(0, 100, len(cw_df))
    
    print("\n[4/7] RUNNING ISOLATION FOREST ENSEMBLE...")
    if len(works_features) > 2:
        model = WorkIsolationForest(feature_cols=['final_amount', 'cost_deviation', 'delay_days'], contamination=0.1)
        model.fit(works_features)
        scored_df = model.score(works_features)
        works_features['iforest_score'] = scored_df['work_if_score']
        print(f"Computed Isolation Forest scores for {len(works_features)} projects.")
        
        # Calculate SHAP Explanations
        print("\n[4b] GENERATING SHAP EXPLANATIONS...")
        explainer = ModelExplainer(model, ['final_amount', 'cost_deviation', 'delay_days'])
        shap_explanations = explainer.explain_instances(works_features)
        
        wf_engine = WhyFlaggedEngine()
        formatted_reasons = wf_engine.format_explanations(shap_explanations)
    else:
        works_features['iforest_score'] = 0.5
        formatted_reasons = [[] for _ in range(len(cw_df))]

    print("\n[5/7] CALCULATING UNIFIED RISK SCORES...")
    risk_engine = UnifiedRiskEngine()
    
    # Create a mock dataframe mimicking the required structure for Risk Engine
    risk_df = pd.DataFrame({
        'work_id': cw_df['work_id'],
        'tabular_anomaly_score': works_features['iforest_score'],
        'vendor_risk_score': np.random.rand(len(cw_df)),
        'network_centrality_score': np.random.rand(len(cw_df)),
        'financial_compliance_score': np.random.rand(len(cw_df)),
        'nlp_splitting_score': np.random.rand(len(cw_df))
    })
    
    signal_cols = {
        'tabular_anomaly': 'tabular_anomaly_score',
        'vendor_network': 'vendor_risk_score',
        'networkx_centrality': 'network_centrality_score',
        'financial_compliance': 'financial_compliance_score',
        'nlp_contract_splitting': 'nlp_splitting_score'
    }
    
    scored_projects = risk_engine.score_projects(risk_df, signal_cols=signal_cols)
    
    print("\n[6/7] SEEDING DATABASE...")
    db = SessionLocal()
    
    # Insert MPs
    for _, row in mp_df.iterrows():
        mp_name = str(row.get('mp_name', 'Unknown'))
        mp_id = str(row.get('mp_id', ''))
        if not mp_id:
            val = mp_name + str(row.get('constituency', ''))
            mp_id = "MP_" + hashlib.md5(val.encode()).hexdigest()[:8]
            
        mp = MP(
            id=mp_id,
            mp_name=mp_name,
            state=str(row.get('state', '')),
            constituency=str(row.get('constituency', '')),
            party=str(row.get('party', '')),
            allocated_amount=float(row.get('allocated_amount', 0)),
            expenditure_amount=float(row.get('expenditure_amount', 0)),
            utilization_rate=float(row.get('utilization_rate', 0)),
            completion_rate=float(row.get('completion_rate', 0))
        )
        # Prevent duplicates
        if not db.query(MP).filter_by(id=mp.id).first():
            db.add(mp)
    
    # Insert Vendors
    if 'vendor_name' in exp_df.columns:
        unique_vendors = exp_df['vendor_name'].dropna().unique()
        for v_name in unique_vendors:
            v_id = "V_" + hashlib.md5(v_name.encode()).hexdigest()[:8]
            vendor = Vendor(
                id=v_id,
                name=v_name,
                total_payout=float(exp_df[exp_df['vendor_name'] == v_name]['amount'].sum()),
                transaction_count=int(len(exp_df[exp_df['vendor_name'] == v_name]))
            )
            if not db.query(Vendor).filter_by(id=vendor.id).first():
                db.add(vendor)
            
    # Insert Projects and Risk Scores
    # We will limit to 500 projects to speed up DB seeding for the MVP
    for i, row in cw_df.iterrows():
        p_id = str(row['work_id'])
        mp_name_proj = str(row.get('mp_name', 'Unknown'))
        mp_const_proj = str(row.get('constituency', ''))
        val_proj = mp_name_proj + mp_const_proj
        linked_mp_id = "MP_" + hashlib.md5(val_proj.encode()).hexdigest()[:8]
        
        project = Project(
            id=p_id,
            mp_id=linked_mp_id,
            work_name=str(row.get('work_description', row.get('work_name', 'Unknown'))),
            work_category=str(row.get('category', 'Other')),
            status=str(row.get('status', 'Completed')),
            sanctioned_amount=float(row.get('final_amount', 0)),
            final_amount=float(row.get('final_amount', 0))
        )
        if not db.query(Project).filter_by(id=project.id).first():
            db.add(project)
        
        # Link Risk Score
        score_data = scored_projects.iloc[i]
        
        # Generate string report
        report_str = "No major anomalies."
        if formatted_reasons and len(formatted_reasons) > i and len(formatted_reasons[i]) > 0:
            report_str = WhyFlaggedEngine().generate_report_string(formatted_reasons[i])
        
        risk = ProjectRiskScore(
            project_id=p_id,
            unified_score=float(score_data['unified_risk_score']),
            risk_tier=str(score_data['risk_tier']),
            tabular_pts=float(score_data['tabular_anomaly_score'] * 25),
            network_pts=float(score_data['vendor_risk_score'] * 25),
            graph_pts=float(score_data['network_centrality_score'] * 20),
            financial_pts=float(score_data['financial_compliance_score'] * 15),
            nlp_pts=float(score_data['nlp_splitting_score'] * 15),
            why_flagged_report=report_str
        )
        db.add(risk)

    db.commit()
    db.close()
    
    print("\n[7/7] PIPELINE COMPLETE!")
    print("Database `nexoras_mvp.db` successfully populated with integration data.")
    print("You can now start the FastAPI server (`cd backend && uvicorn api.main:app --reload`).")

if __name__ == "__main__":
    run()
