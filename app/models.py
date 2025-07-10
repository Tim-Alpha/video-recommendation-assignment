from sqlalchemy import Column, Integer, String, Boolean, Float, DateTime, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    first_name = Column(String)
    last_name = Column(String)
    name = Column(String)
    picture_url = Column(String)
    user_type = Column(String, nullable=True)
    has_evm_wallet = Column(Boolean, default=False)
    has_solana_wallet = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    interactions = relationship("UserInteraction", back_populates="user")
    posts = relationship("Post", back_populates="owner")


class Category(Base):
    __tablename__ = "categories"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    count = Column(Integer, default=0)
    description = Column(Text)
    image_url = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Topic(Base):
    __tablename__ = "topics"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(Text)
    image_url = Column(String)
    slug = Column(String, unique=True, index=True)
    is_public = Column(Boolean, default=True)
    project_code = Column(String, index=True)
    posts_count = Column(Integer, default=0)
    language = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=True)


class Post(Base):
    __tablename__ = "posts"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    is_available_in_public_feed = Column(Boolean, default=True)
    is_locked = Column(Boolean, default=False)
    slug = Column(String, unique=True, index=True)
    identifier = Column(String, unique=True, index=True)
    comment_count = Column(Integer, default=0)
    upvote_count = Column(Integer, default=0)
    view_count = Column(Integer, default=0)
    exit_count = Column(Integer, default=0)
    rating_count = Column(Integer, default=0)
    average_rating = Column(Float, default=0.0)
    share_count = Column(Integer, default=0)
    bookmark_count = Column(Integer, default=0)
    video_link = Column(String)
    thumbnail_url = Column(String)
    gif_thumbnail_url = Column(String)
    contract_address = Column(String, nullable=True)
    chain_id = Column(String, nullable=True)
    chart_url = Column(String, nullable=True)
    base_token_data = Column(JSON, nullable=True)
    tags = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Foreign Keys
    owner_id = Column(Integer, ForeignKey("users.id"))
    category_id = Column(Integer, ForeignKey("categories.id"))
    topic_id = Column(Integer, ForeignKey("topics.id"))
    
    # Relationships
    owner = relationship("User", back_populates="posts")
    category = relationship("Category")
    topic = relationship("Topic")
    interactions = relationship("UserInteraction", back_populates="post")


class UserInteraction(Base):
    __tablename__ = "user_interactions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    post_id = Column(Integer, ForeignKey("posts.id"))
    interaction_type = Column(String)  # 'view', 'like', 'inspire', 'rate', 'bookmark'
    rating_value = Column(Float, nullable=True)  # For rating interactions
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="interactions")
    post = relationship("Post", back_populates="interactions") 