import pandas as pd
from pymongo import MongoClient
import os

# Set this to your MongoDB URI (local or Atlas)
MONGO_URI = os.getenv("MONGO_URI", "mongodb+srv://rubeshm60_db_user:hackathon123@cluster0.og4crwa.mongodb.net/?appName=Cluster0")
DB_NAME = "nexoras_data"

def get_mongo_client():
    return MongoClient(MONGO_URI)

def load_mp_summary_from_mongo() -> pd.DataFrame:
    print(f"\n[☁️ CONNECTING TO MONGODB CLOUD: {DB_NAME}.mp_summary...]")
    client = get_mongo_client()
    db = client[DB_NAME]
    cursor = db["mp_summary"].find({}, {"_id": 0})
    return pd.DataFrame(list(cursor))

def load_completed_works_from_mongo() -> pd.DataFrame:
    print(f"[☁️ FETCHING FROM MONGODB CLOUD: {DB_NAME}.completed_works...]")
    client = get_mongo_client()
    db = client[DB_NAME]
    cursor = db["completed_works"].find({}, {"_id": 0})
    return pd.DataFrame(list(cursor))

def load_recommended_works_from_mongo() -> pd.DataFrame:
    print(f"[☁️ FETCHING FROM MONGODB CLOUD: {DB_NAME}.recommended_works...]")
    client = get_mongo_client()
    db = client[DB_NAME]
    cursor = db["recommended_works"].find({}, {"_id": 0})
    return pd.DataFrame(list(cursor))

def load_expenditures_from_mongo() -> pd.DataFrame:
    print(f"[☁️ FETCHING FROM MONGODB CLOUD: {DB_NAME}.expenditures...]")
    client = get_mongo_client()
    db = client[DB_NAME]
    cursor = db["expenditures"].find({}, {"_id": 0})
    return pd.DataFrame(list(cursor))
