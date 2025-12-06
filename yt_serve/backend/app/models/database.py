"""
Database models using SQLAlchemy
"""
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Float, Text, JSON, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

SQLALCHEMY_DATABASE_URL = "sqlite:///./yt_manager.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class Playlist(Base):
    """Playlist model"""
    __tablename__ = "playlists"
    
    id = Column(Integer, primary_key=True, index=True)
    url = Column(String, unique=True, index=True, nullable=False)
    title = Column(String, nullable=False)
    local_count = Column(Integer, default=0)
    playlist_count = Column(Integer, default=0)
    unavailable_count = Column(Integer, default=0)
    last_download = Column(DateTime, nullable=True)
    last_extract = Column(DateTime, nullable=True)
    excluded_ids = Column(JSON, default=list)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Job(Base):
    """Download/Extract job model"""
    __tablename__ = "jobs"
    
    id = Column(Integer, primary_key=True, index=True)
    playlist_id = Column(Integer, nullable=False)
    job_type = Column(String, nullable=False)  # download, extract, both
    status = Column(String, default="pending")  # pending, running, completed, failed, cancelled
    
    # Overall progress (deprecated, kept for compatibility)
    progress = Column(Float, default=0.0)
    total_items = Column(Integer, default=0)
    completed_items = Column(Integer, default=0)
    failed_items = Column(Integer, default=0)
    
    # Separate download progress
    download_status = Column(String, nullable=True)  # pending, running, completed, failed
    download_total = Column(Integer, default=0)
    download_completed = Column(Integer, default=0)
    download_failed = Column(Integer, default=0)
    download_batch_info = Column(String, nullable=True)  # e.g., "Batch 1/3"
    
    # Separate extraction progress
    extract_status = Column(String, nullable=True)  # pending, running, completed, failed
    extract_total = Column(Integer, default=0)
    extract_completed = Column(Integer, default=0)
    extract_failed = Column(Integer, default=0)
    
    error = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)

# Create tables
Base.metadata.create_all(bind=engine)

# Dependency
def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
