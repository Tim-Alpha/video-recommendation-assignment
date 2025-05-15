from sqlalchemy import Column, Integer, String, Boolean, Float, DateTime, JSON, ForeignKey
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    first_name = Column(String)
    last_name = Column(String)
    username = Column(String)
    twitter_url = Column(String, default="")
    twitter_username = Column(String, default="")
    twitter_profile_url = Column(String, default="")
    email = Column(String)
    gender = Column(String, default="")
    role = Column(String)
    profile_url = Column(String)
    bio = Column(String, default="")
    user_type = Column(String, nullable=True)
    hourly_rate = Column(Float, default=0.0)
    currency = Column(String, default="USD")
    website_url = Column(String, default="")
    instagram_url = Column(String, nullable=True)
    youtube_url = Column(String, nullable=True)
    tictok_url = Column(String, nullable=True)
    isVerified = Column(Boolean, default=False)
    referral_code = Column(String)
    has_wallet = Column(Boolean, default=False)
    last_login = Column(DateTime, nullable=True)
    share_count = Column(Integer, default=0)
    total_reward_points = Column(Integer, default=0)
    referral_point = Column(Integer, default=0)
    referral_count = Column(Integer, default=0)
    total_inspired_user_count = Column(Integer, default=0)
    daily_login_streak = Column(Integer, default=0)
    post_count = Column(Integer, default=0)
    following_count = Column(Integer, default=0)
    follower_count = Column(Integer, default=0)
    is_verified = Column(Boolean, default=False)
    is_online = Column(Boolean, default=False)
    latitude = Column(String, default="")
    longitude = Column(String, default="")

class Post(Base):
    __tablename__ = 'posts'

    id = Column(Integer, primary_key=True)
    category = Column(JSON)
    topic = Column(JSON)
    slug = Column(String)
    title = Column(String)
    identifier = Column(String)
    comment_count = Column(Integer, default=0)
    upvote_count = Column(Integer, default=0)
    view_count = Column(Integer, default=0)
    exit_count = Column(Integer, default=0)
    rating_count = Column(Integer, default=0)
    average_rating = Column(Integer, default=0)
    share_count = Column(Integer, default=0)
    bookmark_count = Column(Integer, default=0)
    video_link = Column(String)
    contract_address = Column(String, default="")
    chain_id = Column(String, default="")
    chart_url = Column(String, default="")
    baseToken = Column(JSON)
    is_locked = Column(Boolean, default=False)
    created_at = Column(DateTime)
    first_name = Column(String)
    last_name = Column(String)
    username = Column(String)
    user_type = Column(String, nullable=True)
    has_evm_wallet = Column(Boolean, default=False)
    has_solana_wallet = Column(Boolean, default=False)
    is_viewed = Column(Boolean, default=False)
    upvoted = Column(Boolean, default=False)
    bookmarked = Column(Boolean, default=False)
    is_available_in_public_feed = Column(Boolean, default=True)
    thumbnail_url = Column(String)
    gif_thumbnail_url = Column(String, default="")
    following = Column(Boolean, default=False)
    picture_url = Column(String)
    post_summary = Column(JSON)
    tags = Column(JSON)
    source_matrix = Column(JSON)

class PostView(Base):
    __tablename__ = 'post_views'
    id = Column(Integer, primary_key=True)
    post_id = Column(Integer, ForeignKey('posts.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    viewed_at = Column(DateTime)

class PostLike(Base):
    __tablename__ = 'post_likes'
    id = Column(Integer, primary_key=True)
    post_id = Column(Integer, ForeignKey('posts.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    liked_at = Column(DateTime)

class PostInspire(Base):
    __tablename__ = 'post_inspires'
    id = Column(Integer, primary_key=True)
    post_id = Column(Integer, ForeignKey('posts.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    inspired_at = Column(DateTime)

class PostRating(Base):
    __tablename__ = 'post_ratings'
    id = Column(Integer, primary_key=True)
    post_id = Column(Integer, ForeignKey('posts.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    rating_percent = Column(Integer, nullable=False)
    rated_at = Column(DateTime)


class UpdatedPostSummary(Base):
    __tablename__ = 'updated_post_summaries'

    id = Column(Integer, primary_key=True)
    post_id = Column(Integer, ForeignKey('posts.id'), nullable=False, unique=True)
    upvote_count = Column(Integer, default=0)
    view_count = Column(Integer, default=0)
    average_rating = Column(Float, default=0.0)
    username = Column(String, nullable=False)
    keywords = Column(JSON, default=[])
    no_of_person_in_video = Column(Integer, default=0)
    estimated_duration = Column(String, default="")
    main_character_gender = Column(String, default="")
    summary = Column(String, nullable=False)
    category = Column(String, nullable=False)