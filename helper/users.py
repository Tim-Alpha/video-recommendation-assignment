import requests
import csv
import time

# API headers
headers = {
    "Flic-Token": "flic_11d3da28e403d182c36a3530453e290add87d0b4a40ee50f17611f180d47956f",
    "Accept": "application/json",
    "User-Agent": "Python Script"
}

# CSV output path
csv_file_path = "username_userid_map.csv"

# Fetch users from 3 pages and store username -> id mapping
all_users = []

for page in range(1, 4):  # Pages 1 to 3
    url = f"https://api.socialverseapp.com/users/get_all?page={page}&page_size=1000"
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        print(f"❌ Error on page {page}: {response.status_code}")
        print(response.text)
        continue

    try:
        data = response.json()
        users = data.get("users", [])
        all_users.extend(users)
        print(f"✅ Page {page}: {len(users)} users fetched.")
    except Exception as e:
        print(f"❌ Failed to parse page {page}: {e}")
    
    time.sleep(1)  # Avoid hitting rate limits

# Write CSV with username and id
with open(csv_file_path, mode='w', newline='', encoding='utf-8') as file:
    writer = csv.DictWriter(file, fieldnames=["username", "user_id"])
    writer.writeheader()
    for user in all_users:
        writer.writerow({
            "username": user.get("username", ""),
            "user_id": user.get("id", "")
        })

print(f"✅ CSV saved to {csv_file_path} with {len(all_users)} users.")


# 🔍 Function to get user ID by username
def get_user_id_by_username(csv_file_path, username):
    """
    Given a username, return the corresponding user ID from CSV.

    Args:
        csv_file_path (str): Path to the CSV containing username-user_id mapping.
        username (str): Username to look up.

    Returns:
        int or None: User ID if found, else None.
    """
    with open(csv_file_path, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            if row["username"] == username:
                return int(row["user_id"])
    return None


# 🧪 Example usage
example_username = "afrobeezy"
user_id = get_user_id_by_username(csv_file_path, example_username)
print(f"User ID for '{example_username}': {user_id}")
