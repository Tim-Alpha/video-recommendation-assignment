from sqlalchemy.orm import Session
from . import models

def get_user(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

def get_all_videos(db: Session):
    return db.query(models.Video).all()

def get_interactions_for_user(db: Session, user_id: int):
    return db.query(models.Interaction).filter(models.Interaction.user_id == user_id).all()
