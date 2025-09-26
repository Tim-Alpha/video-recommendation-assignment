import os
import requests
from dotenv import load_dotenv

load_dotenv()

FLIC_TOKEN = os.getenv("FLIC_TOKEN")
BASE_URL = os.getenv("API_BASE_URL") + "/posts/view?page=1&page_size=1000"

def fetch_videos_from_flic():
    """
    Fetch videos from FLIC API using the token and base URL from .env
    Returns a list of dicts with keys: id, title, category, video_link, thumbnail_url, score
    """
    if not FLIC_TOKEN or not BASE_URL:
        print("❌ FLIC_TOKEN or BASE_URL not set in .env")
        return []

    headers = {"Flic-Token": FLIC_TOKEN}
    try:
        response = requests.get(BASE_URL, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()

        if "posts" not in data:
            print("⚠️ FLIC token valid but unexpected data structure:", data)
            return []

        videos = []
        for post in data["posts"]:
            video_link = post.get("video_link")
            thumbnail_url = post.get("thumbnail_url")
            if not video_link or not thumbnail_url:
                continue

            videos.append({
                "id": post.get("id"),
                "title": post.get("title", "Untitled"),
                "category": post.get("category", {}).get("name", "Unknown"),
                "video_link": video_link,
                "thumbnail_url": thumbnail_url,
                "score": 0
            })

        print(f"✅ FLIC API fetched {len(videos)} videos successfully.")
        return videos

    except requests.exceptions.RequestException as e:
        print("❌ Error fetching videos from FLIC API:", e)
        return []
