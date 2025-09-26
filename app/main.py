from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
import os

from app.database import SessionLocal
from app import crud
from app.data_fetcher import fetch_videos_from_flic

# FastAPI app
app = FastAPI(title="Video Recommendation Engine")

# Frontend setup
frontend_path = os.path.join(os.path.dirname(__file__), "../frontend")
app.mount("/frontend", StaticFiles(directory=frontend_path), name="frontend")

@app.get("/")
async def serve_frontend():
    index_path = os.path.join(frontend_path, "index.html")
    return FileResponse(index_path)

# DB dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Category mapping
MOOD_TO_FLIC_CATEGORY = {
    "Motivation": ["Flic", "SolTok"],
    "Wellness": ["Bloom Scroll"],
    "Health": ["Pumptok"],
    "Focus": ["Vible"]
}

# Personalized feed
@app.get("/feed/")
def get_personalized_feed(username: str, db: Session = Depends(get_db)):
    # 1. Get or create user
    user = crud.get_user(db, username)
    if not user:
        user = crud.create_user(db, username)

    # 2. Fetch videos from FLIC API
    videos = fetch_videos_from_flic()
    if not videos:
        raise HTTPException(status_code=404, detail="No videos available from FLIC API")

    # 3. Attach interaction info
    recommended = []
    for v in videos:
        interacted = crud.has_user_interacted(db, user.id, v["id"])
        recommended.append({
            **v,
            "interacted": interacted
        })

    return {"recommended_videos": recommended}

# Category feed
@app.get("/feed/category")
def get_category_feed(username: str, project_code: str, db: Session = Depends(get_db)):
    # 1. Get or create user
    user = crud.get_user(db, username)
    if not user:
        user = crud.create_user(db, username)

    # 2. Fetch videos from FLIC API
    videos = fetch_videos_from_flic()
    if not videos:
        raise HTTPException(status_code=404, detail="No videos available from FLIC API")

    # 3. Map frontend category to FLIC categories
    mapped_categories = MOOD_TO_FLIC_CATEGORY.get(project_code, [project_code])

    # 4. Filter videos by mapped categories
    filtered = [v for v in videos if v["category"] in mapped_categories]

    print(f"Videos in category '{project_code}': {len(filtered)}")  # debug

    return {"recommended_videos": filtered}
