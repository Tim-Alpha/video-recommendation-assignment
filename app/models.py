from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from .database import Base
from datetime import datetime

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)

class Video(Base):
    __tablename__ = "videos"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    category = Column(String)
    video_link = Column(String, default="")       # <-- new field
    thumbnail_url = Column(String, default="")    # <-- new field

class Interaction(Base):
    __tablename__ = "interactions"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    video_id = Column(Integer, ForeignKey("videos.id"))
    interaction_type = Column(String)  # like/view/inspire/rating
    timestamp = Column(DateTime, default=datetime.utcnow)
