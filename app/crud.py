from sqlalchemy.orm import Session
from app import models

# -------------------------
# User CRUD
# -------------------------
def get_user(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

def create_user(db: Session, username: str):
    user = models.User(username=username)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

# -------------------------
# Video CRUD
# -------------------------
def get_video(db: Session, video_id: str):
    return db.query(models.Video).filter(models.Video.id == video_id).first()

def create_video(db: Session, video: dict):
    db_video = models.Video(
        id=video["id"],
        title=video["title"],
        category=video["category"],
        video_link=video.get("video_link", ""),
        thumbnail_url=video.get("thumbnail_url", ""),
        score=video.get("score", 0),
    )
    db.add(db_video)
    db.commit()
    db.refresh(db_video)
    return db_video

# -------------------------
# Interactions CRUD
# -------------------------
def record_interaction(db: Session, user_id: int, video_id: str, action: str):
    """
    Record a like, view, or watch event for a user.
    If interaction exists, update it.
    """
    interaction = (
        db.query(models.Interaction)
        .filter(models.Interaction.user_id == user_id, models.Interaction.video_id == video_id)
        .first()
    )

    if interaction:
        # Update interaction
        interaction.action = action
    else:
        # New interaction
        interaction = models.Interaction(user_id=user_id, video_id=video_id, action=action)
        db.add(interaction)

    db.commit()
    db.refresh(interaction)
    return interaction

def get_interactions_for_user(db: Session, user_id: int):
    return db.query(models.Interaction).filter(models.Interaction.user_id == user_id).all()

def has_user_interacted(db: Session, user_id: int, video_id: str) -> bool:
    """
    Check if user has interacted with a video.
    """
    return (
        db.query(models.Interaction)
        .filter(models.Interaction.user_id == user_id, models.Interaction.video_id == video_id)
        .first()
        is not None
    )

# -------------------------
# Cold Start Support
# -------------------------
def get_cold_start_videos(db: Session, category: str = None):
    """
    Returns default videos for cold-start users.
    Optionally filtered by category.
    """
    query = db.query(models.Video)
    if category:
        query = query.filter(models.Video.category.ilike(f"%{category}%"))
    return query.limit(10).all()
