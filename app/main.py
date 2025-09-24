from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app import models
import random
from datetime import datetime
import os

# ----------------------
# Create FastAPI app first
# ----------------------
app = FastAPI(title="Video Recommendation Engine")

# ----------------------
# Now mount frontend folder for serving HTML, CSS, JS
# ----------------------
frontend_path = os.path.join(os.path.dirname(__file__), "../frontend")
app.mount("/frontend", StaticFiles(directory=frontend_path), name="frontend")

from fastapi.responses import FileResponse

@app.get("/")
async def serve_frontend():
    index_path = os.path.join(frontend_path, "index.html")
    return FileResponse(index_path)



# ----------------------
# Dependency to get DB session
# ----------------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ----------------------
# Interaction weights for scoring
# ----------------------
INTERACTION_WEIGHTS = {
    "view": 1,
    "like": 3,
    "inspire": 4,
    "rating": 2
}

INTERACTION_TYPES = list(INTERACTION_WEIGHTS.keys())

# ----------------------
# Predefined mood-category mapping for cold start
# ----------------------
MOOD_CATEGORIES = {
    "Motivation": ["Motivational Video 1", "Motivational Video 2"],
    "Wellness": ["Wellness Video", "Meditation Tips"],
    "Health": ["Fitness Tips", "Nutrition Advice"],
    "Focus": ["Study Tips", "Productivity Hacks"]
}

# ----------------------
# Generate random interactions for demo
# ----------------------
def generate_random_interactions(db: Session):
    users = db.query(models.User).all()
    videos = db.query(models.Video).all()

    # Clear previous interactions
    db.query(models.Interaction).delete()
    db.commit()

    for user in users:
        for _ in range(random.randint(2, 5)):
            video = random.choice(videos)
            interaction_type = random.choice(INTERACTION_TYPES)
            interaction = models.Interaction(
                user_id=user.id,
                video_id=video.id,
                interaction_type=interaction_type,
                timestamp=datetime.utcnow()
            )
            db.add(interaction)
    db.commit()

# ----------------------
# Personalized feed with cold-start support
# ----------------------
@app.get("/feed/")
def get_personalized_feed(username: str, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == username).first()

    if not user:
        # Cold-start: create user and return mood-based recommendations
        user = models.User(username=username)
        db.add(user)
        db.commit()
        db.refresh(user)
        # Pick random mood categories for cold start
        recommended_videos = []
        for category, titles in MOOD_CATEGORIES.items():
            for title in titles:
                video = db.query(models.Video).filter(models.Video.title == title).first()
                if video:
                    recommended_videos.append({
                        "id": video.id,
                        "title": video.title,
                        "category": video.category,
                        "score": 0
                    })
        return {"username": username, "recommended_videos": recommended_videos}

    # Generate random interactions for demo users
    generate_random_interactions(db)

    # Calculate video scores
    video_scores = {}
    interactions = db.query(models.Interaction).filter(models.Interaction.user_id == user.id).all()
    for inter in interactions:
        video_scores[inter.video_id] = video_scores.get(inter.video_id, 0) + INTERACTION_WEIGHTS.get(inter.interaction_type, 0)

    # Recommend videos
    all_videos = db.query(models.Video).all()
    recommended = [{"id": v.id, "title": v.title, "category": v.category, "score": video_scores.get(v.id, 0)} for v in all_videos]

    # Sort descending
    recommended.sort(key=lambda x: x["score"], reverse=True)
    return {"username": username, "recommended_videos": recommended}

# ----------------------
# Category-based feed with cold-start support
# ----------------------
@app.get("/feed/category")
def get_category_feed(
    username: str,
    project_code: str = Query(..., alias="project_code"),
    db: Session = Depends(get_db)
):
    user = db.query(models.User).filter(models.User.username == username).first()

    if not user:
        # Cold-start: create user and return mood-based recommendations for this category
        user = models.User(username=username)
        db.add(user)
        db.commit()
        db.refresh(user)
        recommended_videos = []
        titles = MOOD_CATEGORIES.get(project_code, [])
        for title in titles:
            video = db.query(models.Video).filter(models.Video.title == title).first()
            if video:
                recommended_videos.append({"id": video.id, "title": video.title, "score": 0})
        return {"username": username, "category": project_code, "recommended_videos": recommended_videos}

    # Generate random interactions for demo
    generate_random_interactions(db)

    # Filter videos by category
    all_videos = db.query(models.Video).filter(models.Video.category == project_code).all()

    # Calculate scores
    video_scores = {}
    interactions = db.query(models.Interaction).filter(models.Interaction.user_id == user.id).all()
    for inter in interactions:
        video_scores[inter.video_id] = video_scores.get(inter.video_id, 0) + INTERACTION_WEIGHTS.get(inter.interaction_type, 0)

    recommended = [{"id": v.id, "title": v.title, "score": video_scores.get(v.id, 0)} for v in all_videos]

    # Sort descending
    recommended.sort(key=lambda x: x["score"], reverse=True)
    return {"username": username, "category": project_code, "recommended_videos": recommended}
