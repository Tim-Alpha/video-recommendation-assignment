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
    - With `project_code`: Returns personalized feed filtered by category_name == project_code.
    """
    try:
        # Fetch personalized feed without filtering by project_code
        response = await recommendation_service.get_personalized_feed(
            username=username,
            page=page,
            page_size=page_size,
            project_code=None  # Don't filter by project_code here
        )

        # Now check if we need to filter by project_code
        if project_code and isinstance(response, dict) and "recommendations" in response:
            logger.debug(f"Filtering recommendations for project_code: {project_code}")
            
            # Extract the recommendations list from the response
            recommendations_list = response["recommendations"]
            
            # Get available categories for debugging
            available_categories = set(
                rec["details"].get("category_name", "None") 
                for rec in recommendations_list
                if isinstance(rec, dict) and isinstance(rec.get("details"), dict)
            )
            logger.debug(f"Available categories: {available_categories}")
            
            # Filter the recommendations based on project_code
            filtered_recommendations = []
            for rec in recommendations_list:
                if isinstance(rec, dict) and isinstance(rec.get("details"), dict):
                    category = rec["details"].get("category_name")
                    if category is not None:
                        # Case-insensitive comparison with proper whitespace handling
                        if category.strip().lower() == project_code.strip().lower():
                            filtered_recommendations.append(rec)
            
            # Update the recommendations list in the response
            response["recommendations"] = filtered_recommendations
            
            # Log how many recommendations were found after filtering
            logger.debug(f"Found {len(filtered_recommendations)} recommendations after filtering")
        
        return response
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
        # Fetch mood-based recommendations without filtering by project_code
        response = await recommendation_service.get_mood_based_feed(
            mood_id=mood_id,
            page=page,
            page_size=page_size,
            project_code=None  # Don't filter by project_code here
        )
        
        # Now check if we need to filter by project_code
        if project_code and isinstance(response, dict) and "recommendations" in response:
            logger.debug(f"Filtering recommendations for project_code: {project_code}")
            
            # Extract the recommendations list from the response
            recommendations_list = response["recommendations"]
            
            # Get available categories for debugging
            available_categories = set(
                rec["details"].get("category_name", "None") 
                for rec in recommendations_list
                if isinstance(rec, dict) and isinstance(rec.get("details"), dict)
            )
            logger.debug(f"Available categories: {available_categories}")
            
            # Filter the recommendations based on project_code
            filtered_recommendations = []
            for rec in recommendations_list:
                if isinstance(rec, dict) and isinstance(rec.get("details"), dict):
                    category = rec["details"].get("category_name")
                    if category is not None:
                        # Case-insensitive comparison with proper whitespace handling
                        if category.strip().lower() == project_code.strip().lower():
                            filtered_recommendations.append(rec)
            
            # Update the recommendations list in the response
            response["recommendations"] = filtered_recommendations
            
            # Log how many recommendations were found after filtering
            logger.debug(f"Found {len(filtered_recommendations)} recommendations after filtering")
        
        return response
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.exception("Error fetching mood-based feed")
        raise HTTPException(status_code=500, detail="Internal server error")
