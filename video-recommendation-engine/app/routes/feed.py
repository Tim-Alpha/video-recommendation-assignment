from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
import os
import pickle
import requests
from datetime import datetime, date
from model import user_hybrid_embeddings, post_hybrid_embeddings, interactions_df, post_embedding_df

router = APIRouter()


FLIC_TOKEN = os.getenv("FLIC_TOKEN")
API_BASE_URL = os.getenv("API_BASE_URL")
if not FLIC_TOKEN or not API_BASE_URL:
    raise RuntimeError("FLIC_TOKEN and API_BASE_URL must be set in .env file")



def get_user_id(username_param: str):
    try:
        return int(username_param)
    except ValueError:
        headers = {"Flic-Token": FLIC_TOKEN}
        page = 1
        while True:
            resp = requests.get(f"{API_BASE_URL}/users/get_all?page={page}&page_size=1000", headers=headers)
            if resp.status_code != 200:
                break
            data = resp.json()
            users = data.get("users", [])
            if not users:
                break
            for user in users:
                if str(user.get("username", "")).lower() == username_param.lower() or str(user.get("name", "")).lower() == username_param.lower():
                    return user.get("id")
            page += 1
        raise HTTPException(status_code=404, detail=f"User '{username_param}' not found")


def fetch_posts_by_ids(post_ids):
    headers = {"Flic-Token": FLIC_TOKEN}
    posts_found = []
    remaining = set(post_ids)
    page = 1
    while remaining:
        resp = requests.get(f"{API_BASE_URL}/posts/summary/get?page={page}&page_size=1000", headers=headers)
        if resp.status_code != 200:
            raise HTTPException(status_code=502, detail="Failed to fetch posts from Socialverse API")
        data = resp.json()
        posts = data.get("posts", [])
        if not posts:
            break
        for post in posts:
            pid = post.get("id")
            if pid in remaining:
                posts_found.append(post)
                remaining.remove(pid)
        if not remaining:
            break
        page += 1
    posts_dict = {p["id"]: p for p in posts_found}
    ordered_posts = [posts_dict[pid] for pid in post_ids if pid in posts_dict]
    return ordered_posts


@router.get("/feed", response_class=JSONResponse)
def get_feed(username: str, project_code: str = None):


    try:
        user_id = get_user_id(username)
    except HTTPException as e:
        raise e

    if user_id not in user_hybrid_embeddings:
        raise HTTPException(status_code=404, detail=f"User ID {user_id} not found in embeddings")

    import importlib
    if "model" not in globals():
        m = importlib.import_module("model")
        globals()["model"] = m
    else:
        m = globals()["model"]

    if project_code:
        recs = m.final_recommend_from_project(
            user_id, project_code, user_hybrid_embeddings, post_hybrid_embeddings, post_embedding_df, interactions_df,
            top_k_pool=500, top_k_final=100
        )
    else:
        recs = m.recommend_posts_faiss_cosine(
            user_id, user_hybrid_embeddings, post_hybrid_embeddings, interactions_df, top_k=100
        )

    if not recs:
        raise HTTPException(status_code=404, detail="No recommendations found.")

    recommended_ids = [pid for pid, score in recs]
    posts = fetch_posts_by_ids(recommended_ids)
    return posts
