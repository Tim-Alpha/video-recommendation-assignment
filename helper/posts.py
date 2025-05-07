import requests
import csv

# Base API Endpoint and Headers
BASE_URL = "https://api.socialverseapp.com/posts/summary/get"
headers = {
    "Flic-Token": "flic_11d3da28e403d182c36a3530453e290add87d0b4a40ee50f17611f180d47956f"
}

# Transform a single post safely
def transform_post(post):
    raw_category = post.get("category", {})
    # Handle case when category is a list
    if isinstance(raw_category, list):
        category = raw_category[0] if raw_category else {}
    elif isinstance(raw_category, dict):
        category = raw_category
    else:
        category = {}


    topic = post.get("topic", [])
    topic = topic[0] if isinstance(topic, list) and topic else {}

    base_token = post.get("baseToken", {})

    return {
        "id": post.get("id", ""),
        "first_name": post.get("first_name", ""),
        "last_name": post.get("last_name", ""),
        "name": f"{post.get('first_name', '')} {post.get('last_name', '')}".strip(),
        "username": post.get("username", ""),
        "picture_url": post.get("picture_url", ""),
        "user_type": post.get("user_type"),
        "has_evm_wallet": post.get("has_evm_wallet", False),
        "has_solana_wallet": post.get("has_solana_wallet", False),
        "category_id": category.get("id"),
        "category_name": category.get("name"),
        "category_description": category.get("description"),
        "category_image_url": category.get("image_url"),
        "topic_id": topic.get("id"),
        "topic_name": topic.get("name"),
        "title": post.get("title", ""),
        "is_available_in_public_feed": post.get("is_available_in_public_feed", False),
        "is_locked": post.get("is_locked", False),
        "slug": post.get("slug", ""),
        "upvoted": post.get("upvoted", False),
        "bookmarked": post.get("bookmarked", False),
        "following": post.get("following", False),
        "identifier": post.get("identifier", ""),
        "comment_count": post.get("comment_count", 0),
        "upvote_count": post.get("upvote_count", 0),
        "view_count": post.get("view_count", 0),
        "exit_count": post.get("exit_count", 0),
        "rating_count": post.get("rating_count", 0),
        "average_rating": post.get("average_rating", 0),
        "share_count": post.get("share_count", 0),
        "bookmark_count": post.get("bookmark_count", 0),
        "video_link": post.get("video_link", ""),
        "thumbnail_url": post.get("thumbnail_url", ""),
        "gif_thumbnail_url": post.get("gif_thumbnail_url", ""),
        "contract_address": post.get("contract_address", ""),
        "chain_id": post.get("chain_id", ""),
        "chart_url": post.get("chart_url", ""),
        "base_token_address": base_token.get("address", ""),
        "base_token_name": base_token.get("name", ""),
        "base_token_symbol": base_token.get("symbol", ""),
        "base_token_image_url": base_token.get("image_url", ""),
        "created_at": post.get("created_at", 0),
        "tags": ",".join(post.get("tags", []))
    }

# Fetch and accumulate posts from first 3 pages
all_transformed_posts = []
for page in range(1, 4):  # Pages 1 to 3
    print(f"Fetching page {page}...")
    response = requests.get(f"{BASE_URL}?page={page}&page_size=1000", headers=headers)
    if response.status_code != 200:
        print(f"⚠️ Failed to fetch page {page}, status code: {response.status_code}")
        continue

    try:
        data = response.json()
    except Exception as e:
        print(f"❌ Error parsing JSON on page {page}: {e}")
        continue

    posts = data.get("posts", [])
    print(f"✅ Fetched {len(posts)} posts on page {page}")
    all_transformed_posts.extend([transform_post(post) for post in posts])

# Save all posts to CSV
csv_file_path = "all_posts.csv"
if all_transformed_posts:
    with open(csv_file_path, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=all_transformed_posts[0].keys())
        writer.writeheader()
        writer.writerows(all_transformed_posts)
    print(f"✅ CSV saved: {csv_file_path}")
else:
    print("⚠️ No posts to write.")
