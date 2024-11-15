import requests
import json

# Base URL for the API
BASE_URL = "https://api.socialverseapp.com"
TOKEN = "flic_1e01009f9c1a54706f385bcc1993a08fd9647ba8f499572d280654d1c03c47bf"
HEADERS = {"Flic-Token": TOKEN}

def fetch_viewed_posts(page=1, page_size=1000):
    url = f"{BASE_URL}/posts/view?page={page}&page_size={page_size}&resonance_algorithm=resonance_algorithm_cjsvervb7dbhss8bdrj89s44jfjdbsjd0xnjkbvuire8zcjwerui3njfbvsujc5if"
    response = requests.get(url, headers=HEADERS)
    return response.json()

def fetch_liked_posts(page=1, page_size=5):
    url = f"{BASE_URL}/posts/like?page={page}&page_size={page_size}&resonance_algorithm=resonance_algorithm_cjsvervb7dbhss8bdrj89s44jfjdbsjd0xnjkbvuire8zcjwerui3njfbvsujc5if"
    response = requests.get(url, headers=HEADERS)
    return response.json()

def fetch_ratings(page=1, page_size=5):
    url = f"{BASE_URL}/posts/rating?page={page}&page_size={page_size}&resonance_algorithm=resonance_algorithm_cjsvervb7dbhss8bdrj89s44jfjdbsjd0xnjkbvuire8zcjwerui3njfbvsujc5if"
    response = requests.get(url, headers=HEADERS)
    return response.json()

def fetch_posts(page=1, page_size=1000):
    url = f"{BASE_URL}/posts/summary/get?page={page}&page_size={page_size}"
    response = requests.get(url, headers=HEADERS)
    return response.json()

def fetch_all_users(page=1, page_size=1000):
    url = f"{BASE_URL}/users/get_all?page={page}&page_size={page_size}"
    response = requests.get(url, headers=HEADERS)
    return response.json()

# Example of how to fetch and print the data
if __name__ == "__main__":
    viewed_posts = fetch_viewed_posts()
    print(json.dumps(viewed_posts, indent=4))  # Pretty print the JSON response
