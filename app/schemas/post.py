# File: app/schemas/post.py

from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime

class PostBase(BaseModel):
    post_id: str
    project_code: Optional[str] = None
    content: Optional[str] = None
    # --- ADD THIS LINE ---
    thumbnail_url: Optional[str] = None
    video_link: Optional[str] = None

class PostCreate(PostBase):
    pass

class Post(PostBase):
    id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)