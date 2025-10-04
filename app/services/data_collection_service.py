
import httpx
from sqlalchemy.orm import Session
from app.core.config import API_BASE_URL, FLIC_TOKEN
from app.crud import crud_user, crud_post, crud_interaction
from app.schemas.user import UserCreate
from app.schemas.post import PostCreate
import asyncio

async def fetch_and_store_data(db: Session):
    headers = {"Flic-Token": FLIC_TOKEN}
    print(f"DEBUG: Using headers: {headers}")
    print("="*50)
    print("--- STARTING COMPREHENSIVE DATA COLLECTION ---")
    print("="*50)

    # --- SETUP: These maps are the key to solving the ID mismatch problem ---
    api_user_id_to_db_user = {}
    api_post_id_to_db_post = {}

    async with httpx.AsyncClient() as client:
        
        # --- STAGE 1: FETCH USERS AND BUILD THE USER MAP ---
        users_url = f"{API_BASE_URL}/users/get_all?page=1&page_size=1000"
        print(f"\n[STAGE 1] Fetching all users from: {users_url}")
        
        try:
            response = await client.get(users_url, headers=headers, timeout=60.0)
            if response.status_code == 200:
                json_response = response.json()
                users_list = json_response.get("users", [])
                
                print(f"  -> SUCCESS: API returned {len(users_list)} users. Storing and mapping...")
                for user_info in users_list:
                    if user_info and user_info.get("username") and user_info.get("id"):
                        username = user_info["username"]
                        api_user_id = user_info["id"]
                        
                        user = crud_user.get_user_by_username(db, username=username)
                        if not user:
                            user = crud_user.create_user(db, user=UserCreate(username=username))
                            print(f"    - Stored new user: {username}")
                        
                        if user:
                            api_user_id_to_db_user[api_user_id] = user
            else:
                print(f"  -> ERROR fetching users. Status: {response.status_code}")
        except Exception as e:
            print(f"  -> FATAL ERROR during user fetching: {e}")

        # --- STAGE 2: FETCH POSTS AND BUILD THE POST MAP ---
        posts_url = f"{API_BASE_URL}/posts/summary/get?page=1&page_size=1000"
        print(f"\n[STAGE 2] Fetching all posts from: {posts_url}")

        try:
            response = await client.get(posts_url, headers=headers, timeout=60.0)
            if response.status_code == 200:
                json_response = response.json()
                posts_list = json_response.get("posts", [])

                print(f"  -> SUCCESS: API returned {len(posts_list)} posts. Storing and mapping...")
                for post_info in posts_list:
                    if not post_info or not post_info.get("id"):
                        continue
                    
                    api_post_id = post_info["id"]
                    post_id_str = str(api_post_id)
                    
                    post = crud_post.get_post_by_post_id(db, post_id=post_id_str)
                    if not post:
                        post = crud_post.create_post(db, post=PostCreate(
                            post_id=post_id_str,
                            project_code=post_info.get("category", {}).get("name", "Unknown"),
                            content=post_info.get("title", "No Title"),
                            thumbnail_url=post_info.get("thumbnail_url"), # <-- ADD THIS LINE
                            video_link=post_info.get("video_link")
                        ))
                        print(f"    - Stored new post: {post_id_str}")
                    
                    if post:
                        api_post_id_to_db_post[api_post_id] = post
            else:
                print(f"  -> ERROR fetching posts. Status: {response.status_code}")
        except Exception as e:
            print(f"  -> FATAL ERROR during post fetching: {e}")

        # --- STAGE 3: FETCH AND STORE ALL INTERACTIONS USING THE MAPS ---
        interaction_endpoints = {
            "view": "/posts/view",
            "like": "/posts/like",
            "inspire": "/posts/inspire",
            "rating": "/posts/rating",
        }
        
        print("\n[STAGE 3] Fetching and storing all interactions...")
        
        for interaction_type, endpoint in interaction_endpoints.items():
            # Add the required resonance_algorithm parameter
            resonance_param = "resonance_algorithm=resonance_algorithm_cjsvervb7dbhss8bdrj89s44jfjdbsjd0xnjkbvuire8zcjwerui3njfbvsujc5if"
            interaction_url = f"{API_BASE_URL}{endpoint}?page=1&page_size=1000&{resonance_param}"
            print(f"  -> Fetching '{interaction_type}' interactions from: {interaction_url}")
            
            try:
                response = await client.get(interaction_url, headers=headers, timeout=60.0)
                if response.status_code == 200:
                    json_response = response.json()
                    # The key for the list in all these JSONs is "posts"
                    interactions_list = json_response.get("posts", [])
                    
                    print(f"    - SUCCESS: API returned {len(interactions_list)} '{interaction_type}' interactions. Now storing...")
                    
                    for interaction_info in interactions_list:
                        api_user_id = interaction_info.get("user_id")
                        api_post_id = interaction_info.get("post_id")

                        if not api_user_id or not api_post_id:
                            continue

                        # Use our lookup maps to find the correct local objects
                        user_in_db = api_user_id_to_db_user.get(api_user_id)
                        post_in_db = api_post_id_to_db_post.get(api_post_id)

                        if user_in_db and post_in_db:
                            crud_interaction.create_interaction(
                                db, 
                                user_id=user_in_db.id, 
                                post_id=post_in_db.id, 
                                interaction_type=interaction_type
                            )
                            print(f"      - Stored '{interaction_type}' for user '{user_in_db.username}' on post '{post_in_db.post_id}'")
                else:
                    print(f"    - ERROR fetching '{interaction_type}'. Status: {response.status_code}")
            except Exception as e:
                print(f"    - FATAL ERROR during '{interaction_type}' fetching: {e}")

    print("\n" + "="*50)
    print("--- COMPREHENSIVE DATA COLLECTION FINISHED ---")
    print("="*50)