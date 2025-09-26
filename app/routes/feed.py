# app/routes/feed.py
from fastapi import APIRouter, Query, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from app.database import feed_items_collection

router = APIRouter()

# Data models
class FeedItem(BaseModel):
    video_id: int
    title: str
    category: Optional[str] = None

class FeedResponse(BaseModel):
    username: str
    project_code: Optional[str] = None
    feed: List[FeedItem]

# Save feed to MongoDB (synchronous)
def save_feed_to_db(username: str, project_code: Optional[str], feed_list: List[FeedItem]):
    for item in feed_list:
        feed_items_collection.update_one(
            {"username": username, "video_id": item.video_id, "project_code": project_code},
            {"$set": {
                "title": item.title,
                "category": item.category
            }},
            upsert=True
        )

# Generate and save feed
@router.get("/feed", response_model=FeedResponse)
def get_feed(username: str = Query(...), project_code: Optional[str] = None):
    feed_list = [
        FeedItem(video_id=1, title="Motivational Video 1", category="Motivation"),
        FeedItem(video_id=2, title="Inspirational Video 2", category="Inspiration"),
        FeedItem(video_id=3, title="Self-help Video 3", category="Self-help"),
    ]

    save_feed_to_db(username, project_code, feed_list)

    return FeedResponse(username=username, project_code=project_code, feed=feed_list)

# Fetch feed from MongoDB
@router.get("/feed/db", response_model=List[FeedItem])
def get_feed_db(username: str = Query(...), project_code: Optional[str] = None):
    query = {"username": username}
    if project_code:
        query["project_code"] = project_code

    items = list(feed_items_collection.find(query, {"_id": 0}))

    if not items:
        raise HTTPException(status_code=404, detail="Feed not found for the user")

    return [FeedItem(**item) for item in items]
