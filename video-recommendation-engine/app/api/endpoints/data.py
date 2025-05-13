from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from app.services.data_service import data_service
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/refresh-data")
async def refresh_data(background_tasks: BackgroundTasks):
    """
    Refresh all data from external APIs and update the database.
    This is a long-running operation that runs in the background.
    """
    try:
        # Run data fetch in background
        background_tasks.add_task(data_service.fetch_all_data)
        return {"status": "success", "message": "Data refresh started in background"}
    except Exception as e:
        logger.error(f"Error starting data refresh: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to start data refresh")

@router.get("/data-status")
async def get_data_status():
    """
    Get the status of the database and data collection.
    """
    try:
        # Get counts from Neo4j
        user_count = data_service.db.run_query("MATCH (u:User) RETURN count(u) as count")[0]["count"]
        post_count = data_service.db.run_query("MATCH (p:Post) RETURN count(p) as count")[0]["count"]
        interaction_count = data_service.db.run_query("MATCH ()-[r:INTERACTED]->() RETURN count(r) as count")[0]["count"]
        
        return {
            "status": "success",
            "data": {
                "users": user_count,
                "posts": post_count,
                "interactions": interaction_count,
                "last_updated": data_service.db.run_query(
                    "MATCH ()-[r:INTERACTED]->() RETURN max(r.timestamp) as last_updated"
                )[0]["last_updated"]
            }
        }
    except Exception as e:
        logger.error(f"Error getting data status: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get data status")
