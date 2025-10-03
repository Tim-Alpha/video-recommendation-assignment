from fastapi import APIRouter, HTTPException, Query
from typing import Optional
import os
import requests
from pydantic import BaseModel
from predict import predict_posts

# Initialize router
router = APIRouter()
from dotenv import load_dotenv
load_dotenv()
# Environment variables
FLIC_TOKEN = os.getenv("FLIC_TOKEN")
API_BASE_URL = os.getenv("API_BASE_URL")
RESONANCE_ALGORITHM = os.getenv("RESONANCE_ALGORITHM")
PAGE_SIZE = os.getenv("PAGE_SIZE")



print("FLIC TOKEN IS ",FLIC_TOKEN)
print("URL IS ", API_BASE_URL)
# Response model for feeds
class FeedResponse(BaseModel):
    items: list
    page: int
    page_size: int
    total: Optional[int] = None


class UserResponse(BaseModel):
    users: list
    pages: int

class PostResponse(BaseModel):
    posts: list
    pages:int

# # Recommendation Endpoints
# @router.get("/feed", response_model=FeedResponse)
# async def get_personalized_feed(
#     username: str = Query(...),
#     page: int = Query(1, ge=1),
#     page_size: int = Query(100, ge=1, le=1000)
# ):
#     """
#     Get personalized video recommendations for a specific user.
#     Supports pagination with page and page_size parameters.
#     """
#     try:
#         # Construct URL for external API
#         url = f"{API_BASE_URL}/feed?username={username}&page={page}&page_size={page_size}"
#         response = requests.get(url)
#         response.raise_for_status()
        
#         data = response.json()
#         return {
#             "items": data.get("items", []),
#             "page": page,
#             "page_size": page_size,
#             "total": data.get("total")
#         }
#     except requests.RequestException as e:
#         raise HTTPException(status_code=500, detail=f"Failed to fetch feed: {str(e)}")

# @router.get("/feed/category", response_model=FeedResponse)
# async def get_category_feed(
#     username: str = Query(...),
#     project_code: str = Query(...),
#     page: int = Query(1, ge=1),
#     page_size: int = Query(100, ge=1, le=1000)
# ):
#     """
#     Get category-specific video recommendations for a user.
#     Supports pagination with page and page_size parameters.
#     """
#     try:
#         # Construct URL for external API
#         url = f"{API_BASE_URL}/feed?username={username}&project_code={project_code}&page={page}&page_size={page_size}"
#         response = requests.get(url)
#         response.raise_for_status()
        
#         data = response.json()
#         return {
#             "items": data.get("items", []),
#             "page": page,
#             "page_size": page_size,
#             "total": data.get("total")
#         }
#     except requests.RequestException as e:
#         raise HTTPException(status_code=500, detail=f"Failed to fetch category feed: {str(e)}")

# Data Collection Endpoints (Internal Use)
@router.get("/posts/view", response_model=PostResponse)
async def get_viewed_posts():
    """
    Get all viewed posts with pagination.
    """
    all_posts = []
    page = 1
    try:
        while True:
            url = f"{API_BASE_URL}/posts/view?page={page}&page_size={PAGE_SIZE}&resonance_algorithm={RESONANCE_ALGORITHM}"
            response = requests.get(url)
            response.raise_for_status()
            
            data = response.json()
            posts = data.get("posts", [])
            
            if not posts:
                break
                
            all_posts.extend(posts)
            page += 1
            
        return {"posts": all_posts, "pages":page-1}
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch users: {str(e)}")

@router.get("/posts/like", response_model=PostResponse)
async def get_liked_posts():
    """
    Get all liked posts with pagination.
    """
    all_posts = []
    page = 1
    try:
        while True:
            url = f"{API_BASE_URL}/posts/like?page={page}&page_size={PAGE_SIZE}&resonance_algorithm={RESONANCE_ALGORITHM}"
            response = requests.get(url)
            response.raise_for_status()
            
            data = response.json()
            posts = data.get("posts", [])
            
            if not posts:
                break
                
            all_posts.extend(posts)
            page += 1
            
        return {"posts": all_posts, "pages":page-1}
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch users: {str(e)}")

@router.get("/posts/inspire", response_model=PostResponse)
async def get_inspired_posts():
    """
    Get all inspired posts with pagination.
    """
    all_posts = []
    page = 1
    try:
        while True:
            url = f"{API_BASE_URL}/posts/inspire?page={page}&page_size={PAGE_SIZE}&resonance_algorithm={RESONANCE_ALGORITHM}"
            response = requests.get(url)
            response.raise_for_status()
            
            data = response.json()
            posts = data.get("posts", [])
            
            if not posts:
                break
                
            all_posts.extend(posts)
            page += 1
            
        return {"posts": all_posts, "pages":page-1}
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch users: {str(e)}")

@router.get("/posts/rating", response_model=PostResponse)
async def get_rated_posts():
    """
    Get all rated posts with pagination.
    """
    all_posts = []
    page = 1
    try:
        while True:
            url = f"{API_BASE_URL}/posts/rating?page={page}&page_size={PAGE_SIZE}&resonance_algorithm={RESONANCE_ALGORITHM}"
            response = requests.get(url)
            response.raise_for_status()
            
            data = response.json()
            posts = data.get("posts", [])
            
            if not posts:
                break
                
            all_posts.extend(posts)
            page += 1
            
        return {"posts": all_posts, "pages":page-1}
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch users: {str(e)}")

@router.get("/posts/summary/get", response_model=PostResponse)
async def get_all_posts():
    """
    Get all posts with pagination.
    Requires Flic token authentication passed to external API.
    """
    if not FLIC_TOKEN:
        raise HTTPException(status_code=500, detail="FLIC_TOKEN not configured")
    
    all_posts = []
    page = 1
    try:
        while True:
            url = f"{API_BASE_URL}/posts/summary/get?page={page}&page_size={PAGE_SIZE}"
            headers = {"Flic-Token": FLIC_TOKEN}
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            
            data = response.json()
            posts = data.get("posts", [])
            
            if not posts:
                break
                
            all_posts.extend(posts)
            page += 1
            
        return {"posts": all_posts, "pages":page-1}
        
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch users: {str(e)}")

@router.get("/users/get_all", response_model=UserResponse)
async def get_all_users():
    """
    Get all users by looping through pages until users list is empty.
    Requires Flic token authentication passed to external API.
    """
    if not FLIC_TOKEN:
        raise HTTPException(status_code=500, detail="FLIC_TOKEN not configured")
    
    all_users = []
    page = 1
    
    try:
        while True:
            url = f"{API_BASE_URL}/users/get_all?page={page}&page_size={PAGE_SIZE}"
            headers = {"Flic-Token": FLIC_TOKEN}
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            
            data = response.json()
            users = data.get("users", [])
            
            if not users:
                break
                
            all_users.extend(users)
            page += 1
            
        return {"users": all_users, "pages":page-1}
        
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch users: {str(e)}")
    

@router.get("/feed")
async def get_feed(userid: int, project_code: str = None):
    try:
        # Call predict_post with username as user_id and optional project_code as category
        recommendations = predict_posts(user_id=userid, category=project_code)
        return  recommendations
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating recommendations: {str(e)}")