from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
import asyncio

from app.database import get_db, engine
from app.models import Base
from app.services import data_service, recommendation_service
from config import settings

# Create database tables
Base.metadata.create_all(bind=engine)

# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    description="A sophisticated video recommendation system using deep neural networks",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Video Recommendation Engine API",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "video-recommendation-engine"}


@app.get("/feed")
async def get_personalized_feed(
    username: str = Query(..., description="Username to get recommendations for"),
    project_code: Optional[str] = Query(None, description="Optional project code for category-specific feed"),
    limit: int = Query(10, ge=1, le=50, description="Number of recommendations to return"),
    db: Session = Depends(get_db)
):
    """
    Get personalized video recommendations for a user.
    
    - **username**: Username to get recommendations for
    - **project_code**: Optional project code for category-specific recommendations
    - **limit**: Number of recommendations to return (1-50)
    """
    try:
        if project_code:
            # Get category-specific recommendations
            posts = recommendation_service.get_category_feed(db, username, project_code, limit)
        else:
            # Get personalized recommendations
            posts = recommendation_service.get_personalized_feed(db, username, limit)
        
        return {
            "status": "success",
            "post": posts,
            "count": len(posts),
            "username": username,
            "project_code": project_code
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting recommendations: {str(e)}")


@app.post("/sync")
async def sync_external_data(db: Session = Depends(get_db)):
    """
    Sync data from external API to local database.
    This endpoint fetches all data from the external socialverse API.
    """
    try:
        sync_results = await data_service.sync_external_data(db)
        
        if "error" in sync_results:
            raise HTTPException(status_code=500, detail=sync_results["error"])
        
        return {
            "status": "success",
            "message": "Data sync completed successfully",
            "results": sync_results
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error syncing data: {str(e)}")


@app.get("/stats")
async def get_stats(db: Session = Depends(get_db)):
    """Get system statistics"""
    try:
        from app.models import User, Post, UserInteraction, Category, Topic
        
        stats = {
            "users": db.query(User).count(),
            "posts": db.query(Post).count(),
            "interactions": db.query(UserInteraction).count(),
            "categories": db.query(Category).count(),
            "topics": db.query(Topic).count(),
            "last_sync": data_service.last_sync_time.isoformat() if data_service.last_sync_time else None
        }
        
        return {
            "status": "success",
            "stats": stats
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting stats: {str(e)}")


@app.get("/users")
async def get_users(
    limit: int = Query(10, ge=1, le=100, description="Number of users to return"),
    db: Session = Depends(get_db)
):
    """Get list of users"""
    try:
        from app.models import User
        
        users = db.query(User).limit(limit).all()
        
        user_list = []
        for user in users:
            user_list.append({
                "id": user.id,
                "username": user.username,
                "name": user.name,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "picture_url": user.picture_url,
                "user_type": user.user_type,
                "has_evm_wallet": user.has_evm_wallet,
                "has_solana_wallet": user.has_solana_wallet,
                "created_at": user.created_at.isoformat() if user.created_at else None
            })
        
        return {
            "status": "success",
            "users": user_list,
            "count": len(user_list)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting users: {str(e)}")


@app.get("/posts")
async def get_posts(
    limit: int = Query(10, ge=1, le=100, description="Number of posts to return"),
    category_id: Optional[int] = Query(None, description="Filter by category ID"),
    topic_id: Optional[int] = Query(None, description="Filter by topic ID"),
    db: Session = Depends(get_db)
):
    """Get list of posts with optional filtering"""
    try:
        from app.models import Post
        
        query = db.query(Post).filter(Post.is_available_in_public_feed == True)
        
        if category_id:
            query = query.filter(Post.category_id == category_id)
        
        if topic_id:
            query = query.filter(Post.topic_id == topic_id)
        
        posts = query.limit(limit).all()
        
        post_list = []
        for post in posts:
            post_list.append({
                "id": post.id,
                "title": post.title,
                "identifier": post.identifier,
                "slug": post.slug,
                "view_count": post.view_count,
                "upvote_count": post.upvote_count,
                "average_rating": post.average_rating,
                "video_link": post.video_link,
                "thumbnail_url": post.thumbnail_url,
                "category_id": post.category_id,
                "topic_id": post.topic_id,
                "created_at": post.created_at.isoformat() if post.created_at else None
            })
        
        return {
            "status": "success",
            "posts": post_list,
            "count": len(post_list)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting posts: {str(e)}")


@app.get("/categories")
async def get_categories(db: Session = Depends(get_db)):
    """Get list of categories"""
    try:
        from app.models import Category
        
        categories = db.query(Category).all()
        
        category_list = []
        for category in categories:
            category_list.append({
                "id": category.id,
                "name": category.name,
                "count": category.count,
                "description": category.description,
                "image_url": category.image_url,
                "created_at": category.created_at.isoformat() if category.created_at else None
            })
        
        return {
            "status": "success",
            "categories": category_list,
            "count": len(category_list)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting categories: {str(e)}")


@app.get("/topics")
async def get_topics(
    project_code: Optional[str] = Query(None, description="Filter by project code"),
    db: Session = Depends(get_db)
):
    """Get list of topics with optional filtering"""
    try:
        from app.models import Topic
        
        query = db.query(Topic)
        
        if project_code:
            query = query.filter(Topic.project_code == project_code)
        
        topics = query.all()
        
        topic_list = []
        for topic in topics:
            topic_list.append({
                "id": topic.id,
                "name": topic.name,
                "description": topic.description,
                "image_url": topic.image_url,
                "slug": topic.slug,
                "is_public": topic.is_public,
                "project_code": topic.project_code,
                "posts_count": topic.posts_count,
                "language": topic.language,
                "created_at": topic.created_at.isoformat() if topic.created_at else None
            })
        
        return {
            "status": "success",
            "topics": topic_list,
            "count": len(topic_list)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting topics: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 