# app/routes/data_collection.py
from fastapi import APIRouter, HTTPException
import os
import requests
from dotenv import load_dotenv
from app.database import db, users_collection, feed_items_collection

load_dotenv()

router = APIRouter()

FLIC_TOKEN = os.getenv("FLIC_TOKEN", "dummy_token_123")
API_BASE_URL = os.getenv("API_BASE_URL", "https://api.socialverseapp.com")
headers = {"Flic-Token": FLIC_TOKEN}

# Function to fetch data from external API
def fetch_data(endpoint: str):
    url = f"{API_BASE_URL}{endpoint}"
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=str(e))

# Save posts to MongoDB
def save_posts_to_db(posts: list, project_code: str):
    for item in posts:
        feed_items_collection.update_one(
            {
                "username": item.get("username"),
                "video_id": item.get("id"),
                "project_code": project_code
            },
            {"$set": {
                "title": item.get("title", "No title"),
                "category": item.get("category", project_code)
            }},
            upsert=True
        )

# Save users to MongoDB
def save_users_to_db(users: list):
    for user in users:
        users_collection.update_one(
            {"username": user.get("username")},
            {"$set": user},
            upsert=True
        )

# API Endpoints
@router.get("/data/viewed_posts")
def get_viewed_posts():
    endpoint = "/posts/view?page=1&page_size=1000&resonance_algorithm=resonance_algorithm_cjsvervb7dbhss8bdrj89s44jfjdbsjd0xnjkbvuire8zcjwerui3njfbvsujc5if"
    data = fetch_data(endpoint)
    posts = data.get("posts", [])
    save_posts_to_db(posts, project_code="viewed")
    return {"message": f"{len(posts)} viewed posts saved to MongoDB."}

@router.get("/data/liked_posts")
def get_liked_posts():
    endpoint = "/posts/like?page=1&page_size=1000&resonance_algorithm=resonance_algorithm_cjsvervb7dbhss8bdrj89s44jfjdbsjd0xnjkbvuire8zcjwerui3njfbvsujc5if"
    data = fetch_data(endpoint)
    posts = data.get("posts", [])
    save_posts_to_db(posts, project_code="liked")
    return {"message": f"{len(posts)} liked posts saved to MongoDB."}

@router.get("/data/inspired_posts")
def get_inspired_posts():
    endpoint = "/posts/inspire?page=1&page_size=1000&resonance_algorithm=resonance_algorithm_cjsvervb7dbhss8bdrj89s44jfjdbsjd0xnjkbvuire8zcjwerui3njfbvsujc5if"
    data = fetch_data(endpoint)
    posts = data.get("posts", [])
    save_posts_to_db(posts, project_code="inspired")
    return {"message": f"{len(posts)} inspired posts saved to MongoDB."}

@router.get("/data/rated_posts")
def get_rated_posts():
    endpoint = "/posts/rating?page=1&page_size=1000&resonance_algorithm=resonance_algorithm_cjsvervb7dbhss8bdrj89s44jfjdbsjd0xnjkbvuire8zcjwerui3njfbvsujc5if"
    data = fetch_data(endpoint)
    posts = data.get("posts", [])
    save_posts_to_db(posts, project_code="rated")
    return {"message": f"{len(posts)} rated posts saved to MongoDB."}

@router.get("/data/all_posts")
def get_all_posts():
    endpoint = "/posts/summary/get?page=1&page_size=1000"
    data = fetch_data(endpoint)
    posts = data.get("posts", [])
    save_posts_to_db(posts, project_code="all")
    return {"message": f"{len(posts)} posts saved to MongoDB."}

@router.get("/data/all_users")
def get_all_users():
    endpoint = "/users/get_all?page=1&page_size=1000"
    data = fetch_data(endpoint)
    users = data.get("users", [])
    save_users_to_db(users)
    return {"message": f"{len(users)} users saved to MongoDB."}
