from sqlalchemy.orm import Session
from app.crud import crud_post, crud_user, crud_interaction
import random

def get_personalized_feed(db: Session, username: str):
    # --- Start of new debugging block ---
    print("\n" + "="*50)
    print(f"DEBUG: Starting recommendation for user: '{username}'")
    # --- End of new debugging block ---

    user = crud_user.get_user_by_username(db, username=username)

    if not user:
        print("DEBUG: 1. User not found in DB. This is a COLD START.")
        print("="*50 + "\n")
        return crud_post.get_popular_posts(db)

    print(f"DEBUG: 1. Found user '{user.username}' (ID: {user.id}). This is a WARM START.")

    seen_post_ids = crud_interaction.get_user_interaction_post_ids(db, user_id=user.id)
    print(f"DEBUG: 2. User has seen {len(seen_post_ids)} posts with these IDs: {seen_post_ids}")

    liked_categories = crud_interaction.get_user_liked_categories(db, user_id=user.id)
    print(f"DEBUG: 3. User has liked the following categories: {liked_categories}")

    recommendations = []
    recommended_post_ids = set()

    if liked_categories:
        print("DEBUG: 4. Generating recommendations from liked categories...")
        for category in liked_categories:
            print(f"    - Checking category: '{category}'")
            posts_in_category = crud_post.get_posts_by_category(db, category_code=category)
            print(f"    - Found {len(posts_in_category)} posts in this category.")
            for post in posts_in_category:
                if post.id not in seen_post_ids:
                    if post.id not in recommended_post_ids:
                        print(f"      + Recommending post ID {post.id} (from category '{category}')")
                        recommendations.append(post)
                        recommended_post_ids.add(post.id)
                    else:
                        print(f"      - Skipping post ID {post.id} (already in recommendations)")
                else:
                    print(f"      - Skipping post ID {post.id} (user has already seen it)")
    else:
        print("DEBUG: 4. User has no liked categories. Skipping this step.")

    print(f"DEBUG: 5. Recommendations after category step: {len(recommendations)} posts.")

    if len(recommendations) < 20:
        print("DEBUG: 6. Not enough recommendations. Topping up with popular posts.")
        popular_posts = crud_post.get_popular_posts(db, limit=40)
        for post in popular_posts:
            if len(recommendations) >= 20:
                break
            if post.id not in seen_post_ids and post.id not in recommended_post_ids:
                print(f"    + Recommending popular post ID {post.id}")
                recommendations.append(post)
                recommended_post_ids.add(post.id)
            else:
                print(f"    - Skipping popular post ID {post.id} (already seen or recommended)")
    
    print(f"DEBUG: 7. Final total recommendations: {len(recommendations)} posts.")
    print("="*50 + "\n")
    return recommendations[:20]


def get_category_based_feed(db: Session, username: str, project_code: str):
    # This function remains the same
    user = crud_user.get_user_by_username(db, username=username)
    posts_in_category = crud_post.get_posts_by_category(db, category_code=project_code)
    
    if user:
        seen_post_ids = crud_interaction.get_user_interaction_post_ids(db, user_id=user.id)
        unseen_posts = [post for post in posts_in_category if post.id not in seen_post_ids]
        return unseen_posts

    return posts_in_category

# 1. Define the mapping from a mood to video categories (project_code)
MOOD_TO_CATEGORIES = {
    "Inspired": ["Flic", "Gratitube"],
    "Motivated": ["Empowerverse", "SolTok"],
    "Calm": ["Vible", "Wellness"],
    "Curious": ["Tech", "Learn"],
}

def get_mood_based_feed(db: Session, mood: str):
    print(f"DEBUG: Getting mood-based feed for mood: '{mood}'")
    
    # 2. Find the categories that match the selected mood
    target_categories = MOOD_TO_CATEGORIES.get(mood, [])
    if not target_categories:
        print(f"DEBUG: No categories found for mood '{mood}'. Returning popular posts.")
        return crud_post.get_popular_posts(db) # Fallback to popular if mood is unknown
        
    print(f"DEBUG: Mapped mood to categories: {target_categories}")

    # 3. Fetch posts from all matching categories
    recommendations = []
    for category in target_categories:
        posts_in_category = crud_post.get_posts_by_category(db, category_code=category, limit=20)
        recommendations.extend(posts_in_category)

    # 4. Shuffle the results and return a fixed number
    random.shuffle(recommendations)
    print(f"DEBUG: Found {len(recommendations)} posts for the mood. Returning 20.")
    return recommendations[:20]