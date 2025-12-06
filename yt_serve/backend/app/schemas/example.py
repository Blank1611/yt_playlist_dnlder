"""
Example Pydantic schemas
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

# Request schemas
class PlaylistCreate(BaseModel):
    """Schema for creating a playlist"""
    url: str = Field(..., description="YouTube playlist URL")

class PlaylistUpdate(BaseModel):
    """Schema for updating a playlist"""
    title: Optional[str] = None
    excluded_ids: Optional[list[str]] = None

# Response schemas
class PlaylistResponse(BaseModel):
    """Schema for playlist response"""
    id: int
    url: str
    title: str
    playlist_count: int
    local_count: int
    unavailable_count: int
    excluded_ids: list[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True  # For SQLAlchemy models
