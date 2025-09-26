# app/routes/videos.py
from fastapi import APIRouter

router = APIRouter()

@router.get("/videos")
def get_videos():
    return [
        {"video_id": 1, "title": "Video 1"},
        {"video_id": 2, "title": "Video 2"}
    ]
