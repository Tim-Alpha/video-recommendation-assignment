import requests
import pandas as pd
from collections import defaultdict

# Base URLs for viewed and liked
base_urls = {
    "viewed": "https://api.socialverseapp.com/posts/view",
    "liked": "https://api.socialverseapp.com/posts/like"
}

# Parameters common to both endpoints
params = {
    "page_size": 1000,
    "resonance_algorithm": "resonance_algorithm_cjsvervb7dbhss8bdrj89s44jfjdbsjd0xnjkbvuire8zcjwerui3njfbvsujc5if"
}

# Initialize interaction dictionary
interactions = defaultdict(lambda: {"viewed": 0, "liked": 0})

# Loop through viewed and liked actions
for action, base_url in base_urls.items():
    for page in range(1, 4):  # Pages 1 to 3
        params["page"] = page
        response = requests.get(base_url, params=params)
        if response.status_code == 200:
            posts = response.json().get("posts", [])
            for post in posts:
                key = (post["user_id"], post["post_id"])
                interactions[key][action] = 1
        else:
            print(f"Failed to fetch {action} page {page}: {response.status_code}")

# Convert to DataFrame
data = [
    {"user_id": k[0], "post_id": k[1], **v}
    for k, v in interactions.items()
]
df = pd.DataFrame(data)

# Save to CSV
df.to_csv("user_post_interactions.csv", index=False)
print("Saved to user_post_interactions.csv")
