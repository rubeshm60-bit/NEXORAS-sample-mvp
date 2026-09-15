import os
import pandas as pd
from pymongo import MongoClient

# ==========================================
# 1. SETUP YOUR MONGODB CONNECTION
# ==========================================
# Replace this with your actual MongoDB Atlas URI if you have one.
# Example: "mongodb+srv://<username>:<password>@cluster0.mongodb.net/"
MONGO_URI = "mongodb+srv://rubeshm60_db_user:hackathon123@cluster0.og4crwa.mongodb.net/?appName=Cluster0"
DB_NAME = "nexoras_data"

# ==========================================
# 2. RAW CSV DIRECTORY
# ==========================================
DATASET_DIR = r"D:\sih 2026\mplads dataset"

FILES = {
    "mp_summary": "mplads_mp_summary_2026-09-10.csv",
    "completed_works": "mplads_completed_works_2026-09-10.csv",
    "recommended_works": "mplads_recommended_works_2026-09-10.csv",
    "expenditures": "mplads_expenditures_2026-09-10.csv"
}

def upload_csv_to_mongo():
    print(f"Connecting to MongoDB at: {MONGO_URI}")
    try:
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
        # Force a connection check
        client.server_info()
    except Exception as e:
        print("\n[ERROR] Could not connect to MongoDB!")
        print("Please make sure MongoDB is running locally, OR edit this file to paste your MongoDB Atlas URI.")
        print(f"Details: {e}")
        return

    db = client[DB_NAME]

    for collection_name, filename in FILES.items():
        filepath = os.path.join(DATASET_DIR, filename)
        if not os.path.exists(filepath):
            print(f"[WARNING] File not found: {filepath}")
            continue

        print(f"\nProcessing {filename}...")
        
        # Read CSV into Pandas
        df = pd.read_csv(filepath)
        
        # Clean column names (convert to lowercase snake_case for MongoDB)
        df.columns = (df.columns.str.strip()
                      .str.replace(r'\(₹\)', '', regex=True)
                      .str.replace(r'\(%\)', '', regex=True)
                      .str.strip()
                      .str.replace(' ', '_')
                      .str.lower())
        
        # Convert DataFrame to list of dictionaries (JSON format for Mongo)
        records = df.to_dict(orient='records')
        
        # Drop the collection if it exists to avoid duplicates during testing
        db[collection_name].drop()
        
        # Insert into MongoDB
        print(f"Uploading {len(records)} records to collection '{collection_name}'...")
        db[collection_name].insert_many(records)
        print(f"Successfully uploaded {collection_name}!")

    print("\n[SUCCESS] All datasets have been uploaded to MongoDB!")

if __name__ == "__main__":
    upload_csv_to_mongo()
