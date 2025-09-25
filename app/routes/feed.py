from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app import crud, models

router = APIRouter()

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/")
def get_personalized_feed(username: str, db: Session = Depends(get_db)):
    user = crud.get_user(db, username)
    if not user:
        return {"message": f"No user found with username {username}"}
    
    interactions = crud.get_interactions_for_user(db, user.id)
    # Simple placeholder: recommend videos the user has NOT interacted with
    interacted_video_ids = [i.video_id for i in interactions]
    all_videos = crud.get_all_videos(db)
    recommended_videos = [v for v in all_videos if v.id not in interacted_video_ids]

    return {
        "username": username,
        "recommended_videos": [{"id": v.id, "title": v.title, "category": v.category} for v in recommended_videos[:10]]  # top 10
    }

@router.get("/category")
def get_category_feed(username: str, project_code: str, db: Session = Depends(get_db)):
    all_videos = crud.get_all_videos(db)
    category_videos = [v for v in all_videos if v.category.lower() == project_code.lower()]
    return {
        "username": username,
        "category": project_code,
        "recommended_videos": [{"id": v.id, "title": v.title} for v in category_videos[:10]]
    }
