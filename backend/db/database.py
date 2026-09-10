"""
NEXORAS — Module 14: Database Connection
========================================
Handles engine initialization and session management.
Using SQLite for the MVP to avoid infrastructure configuration overhead, 
while maintaining a PostgreSQL-ready structure via SQLAlchemy.
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models import Base

# DB Path resolution
DB_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(DB_DIR, "nexoras_mvp.db")
DATABASE_URL = f"sqlite:///{DB_FILE}"

# Engine & Session
engine = create_engine(
    DATABASE_URL, 
    connect_args={"check_same_thread": False},  # Needed for SQLite + FastAPI if sharing sessions
    echo=False  # Set to True for debugging SQL statements
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    """Create all tables defined in models.py."""
    Base.metadata.create_all(bind=engine)
    print(f"Database initialized at {DB_FILE}")

def get_db():
    """Generator to yield a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
