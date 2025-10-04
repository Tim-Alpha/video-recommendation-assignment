from fastapi import APIRouter, Depends, Query, HTTPException 
from sqlalchemy.orm import Session
from app.api import deps
from typing import List
from app.services import recommendation_service
from app.schemas.post import Post

router = APIRouter()

@router.get("/")
def get_feed(
    username: str,
    project_code: str = None,
    db: Session = Depends(deps.get_db),
):
    if project_code:
        return recommendation_service.get_category_based_feed(
            db=db, username=username, project_code=project_code
        )
    return recommendation_service.get_personalized_feed(db=db, username=username)

# --- NEW ENDPOINT FOR MOOD-BASED FEED ---
@router.get("/mood", response_model=List[Post])
def get_mood_feed(mood: str, db: Session = Depends(deps.get_db)):
    """
    Returns a list of videos based on a selected mood for cold-start users.
    """
    if mood not in recommendation_service.MOOD_TO_CATEGORIES:
        raise HTTPException(status_code=404, detail=f"Mood '{mood}' not found.")
    
    return recommendation_service.get_mood_based_feed(db=db, mood=mood)