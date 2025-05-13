from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.api.endpoints import feed, data
from app.core.config import settings
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("app.log")
    ]
)

logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Video Recommendation Engine API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Set up CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(feed.router, prefix=settings.API_V1_STR, tags=["feed"])
app.include_router(data.router, prefix=settings.API_V1_STR, tags=["data"])

@app.get("/", tags=["status"])
async def root():
    """
    Root endpoint to check if the API is running.
    """
    return {
        "status": "online",
        "message": "Video Recommendation Engine API is running",
        "version": "1.0.0",
        "docs_url": "/docs"
    }

@app.get("/health", tags=["status"])
async def health_check():
    """
    Health check endpoint for monitoring.
    """
    try:
        # Check if model and data are loaded
        from app.models.recommendation import recommendation_system
        if recommendation_system.model is None:
            return {
                "status": "warning",
                "message": "Model not loaded"
            }
        
        # Check database connection
        from app.models.database import neo4j_db
        neo4j_db.run_query("RETURN 1 as test")
        
        return {
            "status": "healthy",
            "message": "All systems operational"
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "message": str(e)
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
