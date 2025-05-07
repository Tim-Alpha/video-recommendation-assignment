import torch
import pandas as pd
from fastapi import FastAPI
from recommender import GNNRecommender
import csv

DATA_DIR = "data/"

def load_user_mapping(path=f"{DATA_DIR}username_userid_map.csv"):
    user_map = {}
    with open(path, mode='r', encoding='utf-8') as f:
        for row in csv.DictReader(f):
            user_map[row["username"]] = int(row["user_id"])
    return user_map

def load_all_posts(path=f"{DATA_DIR}all_posts.csv"):
    return pd.read_csv(path).fillna("")

def safe_int(val):
    try:
        return int(val)
    except:
        return None

def format_post(row):
    return {
        "id": safe_int(row["id"]),
        "owner": {
            "first_name": row["first_name"],
            "last_name": row["last_name"],
            "name": row["name"],
            "username": row["username"],
            "picture_url": row["picture_url"],
            "user_type": row["user_type"] or None,
            "has_evm_wallet": bool(row["has_evm_wallet"]),
            "has_solana_wallet": bool(row["has_solana_wallet"])
        },
        "category": {
            "id": safe_int(row["category_id"]),
            "name": row["category_name"],
            "count": 0,
            "description": row["category_description"],
            "image_url": row["category_image_url"]
        },
        "topic": {
            "id": safe_int(row["topic_id"]),
            "name": row["topic_name"],
            "description": "",
            "image_url": f"https://ui-avatars.com/api/?size=300&name={row['topic_name'].replace(' ', '%20')}&color=fff&background=random" if row["topic_name"] else "",
            "slug": "slug-placeholder",
            "is_public": True,
            "project_code": "flic",
            "posts_count": 0,
            "language": None,
            "created_at": "2025-02-15 15:02:41",
            "owner": {
                "first_name": "Shivam",
                "last_name": "Flic",
                "name": "Shivam Flic",
                "username": "random",
                "profile_url": "https://assets.socialverseapp.com/profile/random1739306567image_cropper_1739306539349.jpg.png",
                "user_type": "hirer"
            }
        },
        "title": row["title"],
        "is_available_in_public_feed": bool(row["is_available_in_public_feed"]),
        "is_locked": bool(row["is_locked"]),
        "slug": row["slug"],
        "upvoted": bool(row["upvoted"]),
        "bookmarked": bool(row["bookmarked"]),
        "following": bool(row["following"]),
        "identifier": row["identifier"],
        "comment_count": safe_int(row["comment_count"]) or 0,
        "upvote_count": safe_int(row["upvote_count"]) or 0,
        "view_count": safe_int(row["view_count"]) or 0,
        "exit_count": safe_int(row["exit_count"]) or 0,
        "rating_count": safe_int(row["rating_count"]) or 0,
        "average_rating": safe_int(row["average_rating"]) or 0,
        "share_count": safe_int(row["share_count"]) or 0,
        "bookmark_count": safe_int(row["bookmark_count"]) or 0,
        "video_link": row["video_link"],
        "thumbnail_url": row["thumbnail_url"],
        "gif_thumbnail_url": row["gif_thumbnail_url"],
        "contract_address": row["contract_address"],
        "chain_id": row["chain_id"],
        "chart_url": row["chart_url"],
        "baseToken": {
            "address": row["base_token_address"],
            "name": row["base_token_name"],
            "symbol": row["base_token_symbol"],
            "image_url": row["base_token_image_url"]
        },
        "created_at": safe_int(row["created_at"]) or 0,
        "tags": row["tags"].split(",") if row["tags"] else []
    }

def recommend_posts(model, graph_data, user_id, k=5, category_id=None):
    u_idx = user2idx.get(user_id)
    if u_idx is None:
        raise ValueError("User not in model")

    with torch.no_grad():
        x_dict = model(graph_data)
        user_emb = x_dict["user"][u_idx].unsqueeze(0)
        post_emb = x_dict["post"]
        scores = (user_emb * post_emb).sum(dim=1).cpu().numpy()

        seen = set(interactions[interactions["user_id"] == user_id]["p_idx"])
        candidates = [(i, s) for i, s in enumerate(scores) if i not in seen]

        inv_post = {v: k for k, v in post2idx.items()}
        sorted_posts = sorted(candidates, key=lambda x: x[1], reverse=True)
        ids = [int(inv_post[i]) for i, _ in sorted_posts]

        if category_id:
            filtered = [
                pid for pid in ids
                if safe_int(all_posts[all_posts["id"] == pid]["category_id"].values[0]) == int(category_id)
            ]
            return filtered[:k] if len(filtered) >= k else filtered + ids[:k - len(filtered)]

        return ids[:k]

# Load global data
all_posts = load_all_posts()
user_mapping = load_user_mapping()
checkpoint = torch.load(f"{DATA_DIR}multi_rel_gnn_model.pth", weights_only=False)
graph_data = torch.load(f"{DATA_DIR}graph_data.pt", weights_only=False)

model = GNNRecommender(hidden_dim=128)
model.load_state_dict(checkpoint["model_state_dict"])
model.eval()

user2idx = checkpoint["user2idx"]
post2idx = checkpoint["post2idx"]

interactions = pd.read_csv(f"{DATA_DIR}user_post_interactions.csv")
interactions["u_idx"] = interactions["user_id"].map(user2idx)
interactions["p_idx"] = interactions["post_id"].map(post2idx)

app = FastAPI()

@app.get("/feed")
def get_feed(username: str = None, project_code: int = None):
    try:
        k = 10
        if username and username in user_mapping:
            user_id = user_mapping[username]
            top_ids = recommend_posts(model, graph_data, user_id, k=k, category_id=project_code)
        else:
            raise ValueError("Fallback")

        records = all_posts[all_posts["id"].isin(top_ids)].to_dict(orient="records")
        return {"status": "success", "post": [format_post(pd.Series(r)) for r in records]}
    except:
        fallback = all_posts.sample(10).to_dict(orient="records")
        return {"status": "success", "post": [format_post(pd.Series(r)) for r in fallback]}
