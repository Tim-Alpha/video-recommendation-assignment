from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional
from app.services.recommendation_service import recommendation_service
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/feed", summary="Get personalized or category-based video recommendations")
async def get_feed(
    username: str = Query(..., description="Username to get recommendations for"),
    page: int = Query(1, description="Page number (starting from 1)", ge=1),
    page_size: int = Query(10, description="Number of items per page", ge=1, le=100),
    project_code: Optional[str] = Query(None, description="Optional category/project code")
):
    """
    Returns video recommendations for a user.
    
    - Without `project_code`: Returns personalized feed.
    - With `project_code`: Returns category-filtered feed.
    """
    try:
        recommendations = await recommendation_service.get_personalized_feed(
            username=username,
            page=page,
            page_size=page_size,
            project_code=project_code
        )
        return recommendations
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.exception("Error fetching recommendations")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/mood-feed", summary="Get cold start (mood-based) recommendations")
async def get_mood_feed(
    mood_id: int = Query(..., description="Mood ID for cold start recommendations", ge=1),
    page: int = Query(1, description="Page number", ge=1),
    page_size: int = Query(10, description="Number of items per page", ge=1, le=100),
    project_code: Optional[str] = Query(None, description="Optional category/project code")
):
    """
    Returns video recommendations based on mood (for new users).
    
    Used when `username` is not known (cold start scenario).
    """
    try:
        recommendations = await recommendation_service.get_mood_based_feed(
            mood_id=mood_id,
            page=page,
            page_size=page_size,
            project_code=project_code
        )
        return recommendations
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.exception("Error fetching mood-based feed")
        raise HTTPException(status_code=500, detail="Internal server error")
