import os
import hashlib
import pandas as pd
from sqlalchemy.orm import Session
from backend.db.database import SessionLocal, engine
from backend.db.models import Vendor, VendorRiskProfile
from backend.engine.vendor_intelligence import VendorNetworkIntelligence
from backend.ingestion.mongo_fetch import load_expenditures_from_mongo

def fix_vendor_profiles():
    print("Loading expenditures from MongoDB...")
    exp_df = load_expenditures_from_mongo()
    
    print("Running Vendor Intelligence Engine...")
    vendor_intel = VendorNetworkIntelligence()
    vendor_intel.build_profiles(exp_df)
    
    print("Updating SQLite Database...")
    db = SessionLocal()
    
    # Ensure vendors are committed
    if vendor_intel.vendor_profiles_df is not None and not vendor_intel.vendor_profiles_df.empty:
        for _, vrow in vendor_intel.vendor_profiles_df.iterrows():
            v_name = str(vrow['vendor'])
            v_id = "V_" + hashlib.md5(v_name.encode()).hexdigest()[:8]
            
            # Create vendor if missing
            if not db.query(Vendor).filter_by(id=v_id).first():
                v_exp = exp_df[exp_df['vendor'] == v_name] if 'vendor' in exp_df.columns else exp_df[exp_df['vendor_name'] == v_name]
                mp_count = int(v_exp['mp_name'].nunique()) if 'mp_name' in v_exp.columns else 0
                vendor = Vendor(
                    id=v_id, name=v_name,
                    total_payout=float(vrow['total_payout']),
                    transaction_count=int(vrow['transaction_count']),
                    mp_count=mp_count
                )
                db.add(vendor)
                
        db.commit() # COMMIT VENDORS FIRST
        
        count = 0
        for _, vrow in vendor_intel.vendor_profiles_df.iterrows():
            v_name = str(vrow['vendor'])
            v_id = "V_" + hashlib.md5(v_name.encode()).hexdigest()[:8]
            
            # Check if profile exists, if not create it
            profile = db.query(VendorRiskProfile).filter_by(vendor_id=v_id).first()
            if not profile:
                vrp = VendorRiskProfile(
                    vendor_id=v_id,
                    risk_score=float(vrow['vendor_risk_score']),
                    risk_tier=str(vrow['risk_tier']),
                    flags=str(vrow['risk_flags'])
                )
                db.add(vrp)
                count += 1
            else:
                # Update existing
                profile.risk_score = float(vrow['vendor_risk_score'])
                profile.risk_tier = str(vrow['risk_tier'])
                profile.flags = str(vrow['risk_flags'])
                
        db.commit()
        print(f"Successfully added/updated {count} Vendor Risk Profiles!")
        
    db.close()

if __name__ == "__main__":
    fix_vendor_profiles()
