from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from app.data import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, nullable=True)
    interactions = relationship("Interaction", back_populates="user")

class Post(Base):
    __tablename__ = "posts"
    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(String, unique=True, index=True)
    title = Column(String)
    category = Column(String)
    mood = Column(String)
    rating = Column(Float)
    interactions = relationship("Interaction", back_populates="post")

class Interaction(Base):
    __tablename__ = "interactions"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    post_id = Column(Integer, ForeignKey("posts.id"))
    interaction_type = Column(String)  # view / like / inspire / rating
    value = Column(Float, nullable=True)  # for rating or optional weight

    user = relationship("User", back_populates="interactions")
    post = relationship("Post", back_populates="interactions")
