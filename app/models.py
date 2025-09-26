# app/models.py
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

# Feed Item model for API validation
class FeedItem(BaseModel):
    video_id: int
    title: str
    category: Optional[str] = None

# Feed response model
class FeedResponse(BaseModel):
    username: str
    project_code: Optional[str] = None
    feed: list[FeedItem]

# User model for MongoDB
class User(BaseModel):
    username: str
    created_at: Optional[datetime] = None

# Video model
class Video(BaseModel):
    id: int
    title: str
    category: Optional[str] = None

"hello"