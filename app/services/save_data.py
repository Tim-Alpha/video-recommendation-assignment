import os
import json
import requests
from dotenv import load_dotenv
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.data import SessionLocal
from app.models import model

load_dotenv()

BASE_URL = os.getenv("API_BASE_URL")
FLIC_TOKEN = os.getenv("FLIC_TOKEN")
HEADERS = {"Flic-Token": FLIC_TOKEN}
PAGE_SIZE = 1000
RES_ALGO = "resonance_algorithm_cjsvervb7dbhss8bdrj89s44jfjdbsjd0xnjkbvuire8zcjwerui3njfbvsujc5if"

ENDPOINTS = {
    "view": "posts/view",
    "like": "posts/like",
    "inspire": "posts/inspire",
    "rating": "posts/rating",
    "summary": "posts/summary/get",
    "users": "users/get_all"
}

# --- Fetch Functions ---
def fetch_paginated(endpoint: str):
    page = 1
    all_records = []

    while True:
        params = {"page": page, "page_size": PAGE_SIZE}
        if endpoint in ["view", "like", "inspire", "rating"]:
            params["resonance_algorithm"] = RES_ALGO

        try:
            response = requests.get(f"{BASE_URL}/{endpoint}", headers=HEADERS, params=params, timeout=15)
            print(f"Fetching {endpoint}, page {page}, status {response.status_code}")
            response.raise_for_status()
            data = response.json()
            print("Top-level keys in JSON:", data.keys())

            # Extract records
            records = data.get("users") if endpoint == "users" else data.get("posts")
            if not records:
                print(f"No more records found for {endpoint} on page {page}")
                break

            all_records.extend(records)
            print(f"Fetched {len(records)} records from page {page} of {endpoint}")

            if len(records) < PAGE_SIZE:
                break
            page += 1

        except Exception as e:
            print(f"Error fetching {endpoint} page {page}: {e}")
            break

    print(f"Total {endpoint} records fetched: {len(all_records)}\n")
    return all_records

def fetch_all_data():
    all_data = {}
    for name, ep in ENDPOINTS.items():
        all_data[name] = fetch_paginated(ep)
    return all_data

# --- Save Functions ---
def save_data_to_json(filename="socialverse_data.json"):
    data = fetch_all_data()
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)
    print(f"Data saved to {filename}")
    return data

def save_data_to_db(data: dict):
    db: Session = SessionLocal()
    try:
        for u in data.get("users", []):
            if not isinstance(u, dict):
                continue
            username = u.get("username")
            email = u.get("email")
            if not username or not email:
                continue

            if db.query(model.User).filter(
                (model.User.username == username) | (model.User.email == email)
            ).first():
                continue

            db.add(model.User(username=username, email=email))
        seen_post_ids = set()
        for key in ["view", "like", "inspire", "rating", "summary"]:
            for p in data.get(key, []):
                if not isinstance(p, dict):
                    continue
                post_id = p.get("post_id") or p.get("id")
                if not post_id or post_id in seen_post_ids:
                    continue

                seen_post_ids.add(post_id)

                category = p.get("category")
                mood = p.get("mood")

                db.add(model.Post(
                    post_id=post_id,
                    title=p.get("title"),
                    category=json.dumps(category) if isinstance(category, (dict, list)) else category,
                    mood=json.dumps(mood) if isinstance(mood, (dict, list)) else mood,
                    rating=p.get("rating")
                ))

        db.commit()
        print(" All data saved to DB successfully!")
    except IntegrityError as e:
        db.rollback()
        print("IntegrityError:", e)
    except Exception as e:
        db.rollback()
        print(" Error saving data to DB:", e)
    finally:
        db.close()

# --- Main ---
if __name__ == "__main__":
    data = save_data_to_json()
    save_data_to_db(data)





