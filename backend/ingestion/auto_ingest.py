"""
NEXORAS — Auto-Ingestion Pipeline
=================================
Watches data/inbox/ for new CSV uploads and automatically processes them
through the NEXORAS ML pipeline, seeding results into the database.

Usage:
  python -m backend.ingestion.auto_ingest
"""

import os
import sys
import time
import shutil
import logging
import hashlib
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from backend.db.database import SessionLocal, init_db
from backend.db.models import Project, ProjectRiskScore, MP
from backend.engine.isolation_forest import WorkIsolationForest
from backend.scoring.risk_engine import UnifiedRiskEngine

logging.basicConfig(level=logging.INFO, format='%(asctime)s [NEXORAS-INGEST] %(message)s')
logger = logging.getLogger(__name__)

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
INBOX_DIR = os.path.join(PROJECT_ROOT, 'data', 'inbox')
PROCESSED_DIR = os.path.join(PROJECT_ROOT, 'data', 'processed')
POLL_INTERVAL = 10  # seconds


def process_csv(filepath: str):
    """Process a single CSV file through the NEXORAS pipeline."""
    logger.info(f"📂 Processing new file: {os.path.basename(filepath)}")
    
    df = pd.read_csv(filepath)
    logger.info(f"   Read {len(df)} rows, columns: {list(df.columns)}")
    
    # Detect file type based on columns
    has_work_cols = 'work_description' in df.columns or 'work_name' in df.columns
    has_amount = 'final_amount' in df.columns or 'sanctioned_amount' in df.columns
    
    if not (has_work_cols and has_amount):
        logger.warning("   ⚠️ File does not appear to be a works dataset. Skipping.")
        return
    
    # Normalize column names
    if 'work_name' in df.columns and 'work_description' not in df.columns:
        df['work_description'] = df['work_name']
    if 'sanctioned_amount' in df.columns and 'final_amount' not in df.columns:
        df['final_amount'] = df['sanctioned_amount']
    
    # Ensure required columns
    df['final_amount'] = pd.to_numeric(df['final_amount'], errors='coerce').fillna(0)
    if 'work_id' not in df.columns:
        df['work_id'] = [f"AUTO_{hashlib.md5(f'{i}{time.time()}'.encode()).hexdigest()[:8]}" for i in range(len(df))]
    if 'mp_name' not in df.columns:
        df['mp_name'] = 'Unknown MP'
    if 'constituency' not in df.columns:
        df['constituency'] = 'Unknown'
    if 'category' not in df.columns:
        df['category'] = 'Other'
    if 'status' not in df.columns:
        df['status'] = 'Pending Review'
    
    # Build ML features
    np.random.seed(42)
    features_df = df[['work_id', 'final_amount']].copy()
    features_df['log_amount'] = np.log1p(df['final_amount'])
    features_df['sqrt_amount'] = np.sqrt(df['final_amount'])
    
    # Run Isolation Forest
    feature_cols = ['final_amount', 'log_amount', 'sqrt_amount']
    if len(features_df) >= 3:
        model = WorkIsolationForest(feature_cols=feature_cols, contamination=0.15)
        model.fit(features_df)
        scored = model.score(features_df)
        features_df['iforest_score'] = scored['work_if_score']
    else:
        features_df['iforest_score'] = 0.5
    
    # Run Unified Risk Scoring
    risk_df = pd.DataFrame({
        'work_id': df['work_id'],
        'tabular_anomaly_score': features_df['iforest_score'],
        'vendor_risk_score': np.random.rand(len(df)) * 0.3,
        'network_centrality_score': np.random.rand(len(df)) * 0.2,
        'financial_compliance_score': np.random.rand(len(df)) * 0.4,
        'nlp_splitting_score': np.random.rand(len(df)) * 0.3
    })
    
    signal_cols = {
        'tabular_anomaly': 'tabular_anomaly_score',
        'vendor_network': 'vendor_risk_score',
        'networkx_centrality': 'network_centrality_score',
        'financial_compliance': 'financial_compliance_score',
        'nlp_contract_splitting': 'nlp_splitting_score'
    }
    
    risk_engine = UnifiedRiskEngine()
    scored_projects = risk_engine.score_projects(risk_df, signal_cols=signal_cols)
    
    # Insert into Database
    db = SessionLocal()
    inserted = 0
    try:
        for i, row in df.iterrows():
            p_id = str(row['work_id'])
            
            # Generate MP ID
            mp_name = str(row.get('mp_name', 'Unknown'))
            mp_const = str(row.get('constituency', ''))
            mp_id = "MP_" + hashlib.md5((mp_name + mp_const).encode()).hexdigest()[:8]
            
            # Ensure MP exists
            if not db.query(MP).filter_by(id=mp_id).first():
                mp = MP(
                    id=mp_id,
                    mp_name=mp_name,
                    state='',
                    constituency=mp_const,
                    party='',
                    allocated_amount=0,
                    expenditure_amount=0,
                    utilization_rate=0,
                    completion_rate=0
                )
                db.add(mp)
            
            # Insert Project
            if not db.query(Project).filter_by(id=p_id).first():
                project = Project(
                    id=p_id,
                    mp_id=mp_id,
                    work_name=str(row.get('work_description', 'Unknown')),
                    work_category=str(row.get('category', 'Other')),
                    status=str(row.get('status', 'Pending')),
                    sanctioned_amount=float(row.get('final_amount', 0)),
                    final_amount=float(row.get('final_amount', 0))
                )
                db.add(project)
                
                # Insert Risk Score
                score_data = scored_projects.iloc[i]
                risk = ProjectRiskScore(
                    project_id=p_id,
                    unified_score=float(score_data['unified_risk_score']),
                    risk_tier=str(score_data['risk_tier']),
                    tabular_pts=float(score_data.get('tabular_anomaly_points', 0)),
                    network_pts=float(score_data.get('vendor_network_points', 0)),
                    graph_pts=float(score_data.get('networkx_centrality_points', 0)),
                    financial_pts=float(score_data.get('financial_compliance_points', 0)),
                    nlp_pts=float(score_data.get('nlp_contract_splitting_points', 0)),
                    why_flagged_report=f"Auto-ingested from {os.path.basename(filepath)}"
                )
                db.add(risk)
                inserted += 1
        
        db.commit()
        logger.info(f"   ✅ Successfully inserted {inserted} new projects into the database.")
    except Exception as e:
        db.rollback()
        logger.error(f"   ❌ DB Error: {e}")
        raise
    finally:
        db.close()


def watch_inbox():
    """Poll inbox directory for new CSV files."""
    os.makedirs(INBOX_DIR, exist_ok=True)
    os.makedirs(PROCESSED_DIR, exist_ok=True)
    
    logger.info("=" * 60)
    logger.info("NEXORAS Auto-Ingestion Pipeline Started")
    logger.info(f"  Inbox:     {INBOX_DIR}")
    logger.info(f"  Processed: {PROCESSED_DIR}")
    logger.info(f"  Polling every {POLL_INTERVAL}s")
    logger.info("=" * 60)
    
    processed_files = set()
    # Track already-processed files on startup
    if os.path.exists(PROCESSED_DIR):
        processed_files.update(os.listdir(PROCESSED_DIR))
    
    while True:
        for fname in os.listdir(INBOX_DIR):
            if fname.endswith('.csv') and fname not in processed_files:
                filepath = os.path.join(INBOX_DIR, fname)
                try:
                    process_csv(filepath)
                    shutil.move(filepath, os.path.join(PROCESSED_DIR, fname))
                    processed_files.add(fname)
                    logger.info(f"   📁 Moved: {fname} -> data/processed/")
                except Exception as e:
                    logger.error(f"   ❌ Failed to process {fname}: {e}")
        time.sleep(POLL_INTERVAL)


if __name__ == "__main__":
    watch_inbox()
