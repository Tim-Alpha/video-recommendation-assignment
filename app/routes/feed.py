from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app import crud
from app.data_fetcher import fetch_videos_from_flic

router = APIRouter()

# DB dependency
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
        user = crud.create_user(db, username)

    all_videos = fetch_videos_from_flic()
    interactions = crud.get_interactions_for_user(db, user.id)
    interacted_video_ids = [i.video_id for i in interactions] if interactions else []

    recommended = []
    for v in all_videos:
        if v["id"] not in interacted_video_ids:
            v["interacted"] = False
            recommended.append(v)

    # Cold-start fallback
    if not recommended:
        recommended = crud.get_cold_start_videos(db)
        for v in recommended:
            v["interacted"] = False

    return {"username": username, "recommended_videos": recommended[:10]}

@router.get("/category")
def get_category_feed(username: str, project_code: str, db: Session = Depends(get_db)):
    user = crud.get_user(db, username)
    if not user:
        user = crud.create_user(db, username)

    all_videos = fetch_videos_from_flic()
    interactions = crud.get_interactions_for_user(db, user.id)
    interacted_video_ids = [i.video_id for i in interactions] if interactions else []

    category_videos = []
    for v in all_videos:
        if v["category"].lower() == project_code.lower() and v["id"] not in interacted_video_ids:
            v["interacted"] = False
            category_videos.append(v)

    # Cold-start fallback
    if not category_videos:
        category_videos = crud.get_cold_start_videos(db, category=project_code)
        for v in category_videos:
            v["interacted"] = False

    return {"username": username, "category": project_code, "recommended_videos": category_videos[:10]}
