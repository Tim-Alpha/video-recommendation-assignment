from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import declarative_base
from datetime import datetime
from app.db.base_class import Base


class Interaction(Base):
    __tablename__ = "interactions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    post_id = Column(Integer, ForeignKey("posts.id"))
    interaction_type = Column(String, index=True)  # e.g., 'view', 'like', 'inspire', 'rating'
    created_at = Column(DateTime, default=datetime.utcnow)