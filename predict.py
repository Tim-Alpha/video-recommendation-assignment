from recommendation_engine import RecommendationEngine
from database_manager import load_all_posts
import json
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def predict_posts(user_id, category=None, num_recommendations=10):
    """
    Predict recommended posts for a user and return them in the specified JSON format.
    
    Args:
        user_id (int): ID of the user to get recommendations for
        category (str, optional): Category to filter recommendations
        num_recommendations (int): Number of posts to recommend
    
    Returns:
        dict: JSON response with recommended posts in the specified format
    """
    try:
        # Initialize recommendation engine
        engine = RecommendationEngine()
        
        # Get recommended post IDs
        recommended_post_ids = engine.recommend_posts(user_id, category, num_recommendations)
        logging.info(f"Recommended post IDs for user {user_id}" + 
                     (f" in category {category}" if category else "") + 
                     f": {recommended_post_ids}")
        
        # Load all posts from database
        posts_data = load_all_posts()
        
        # Handle case where posts_data is a dictionary
        if isinstance(posts_data, dict):
            logging.info(f"posts_data is a dictionary with keys: {list(posts_data.keys())}")
            # Try common keys that might contain the posts list
            for key in ["posts", "data", "results"]:
                if key in posts_data and isinstance(posts_data[key], list):
                    posts_data = posts_data[key]
                    logging.info(f"Extracted posts list from key '{key}'")
                    break
            else:
                logging.error(f"No valid posts list found in dictionary: {posts_data.keys()}")
                return {"status": "error", "message": "No valid posts list found in posts_data"}
        
        # Validate posts_data is a list
        if not isinstance(posts_data, list):
            logging.error(f"posts_data is not a list: {type(posts_data)}")
            return {"status": "error", "message": "Invalid posts data format"}
        
        # Log sample post data for debugging
        if posts_data:
            logging.debug(f"Sample post data: {posts_data[0]}")
        
        # Filter posts that match recommended IDs
        matching_posts = []
        for post in posts_data:
            try:
                if not isinstance(post, dict):
                    logging.warning(f"Skipping non-dict post: {post}")
                    continue
                if post.get('id') in recommended_post_ids:
                    matching_posts.append(post)
            except Exception as e:
                logging.warning(f"Error processing post: {e}")
                continue
        
        # Transform each post to the required format
        formatted_posts = []
        for post in matching_posts:
            try:
                formatted_post = {
                    "id": post["id"],
                    "owner": {
                        "first_name": post.get("first_name", ""),
                        "last_name": post.get("last_name", ""),
                        "name": f"{post.get('first_name', '')} {post.get('last_name', '')}".strip(),
                        "username": post.get("username", ""),
                        "picture_url": post.get("picture_url", ""),
                        "user_type": post.get("user_type", None),
                        "has_evm_wallet": post.get("has_evm_wallet", False),
                        "has_solana_wallet": post.get("has_solana_wallet", False)
                    },
                    "category": {
                        "id": post["category"].get("id", 0),
                        "name": post["category"].get("name", ""),
                        "count": post["category"].get("count", 0),
                        "description": post["category"].get("description", ""),
                        "image_url": post["category"].get("image_url", "")
                    },
                    "topic": post.get("topic", []),
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
                    "baseToken": post.get("baseToken", {
                        "address": "",
                        "name": "",
                        "symbol": "",
                        "image_url": ""
                    }),
                    "created_at": post.get("created_at", 0),
                    "tags": post.get("tags", [])
                }
                formatted_posts.append(formatted_post)
            except Exception as e:
                logging.warning(f"Error formatting post {post.get('id', 'unknown')}: {e}")
                continue
        
        # Return formatted JSON response
        return {
            "status": "success",
            "post": formatted_posts
        }
    
    except Exception as e:
        logging.error(f"Error in predict_posts: {e}")
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    # Example usage
    user_id = 5
    category = "Motivation"  # Set to None for no category filter
    num_recommendations = 10
    
    # Call predict_posts with all parameters
    # recommended_posts = predict_posts(user_id, category, num_recommendations)
    recommended_posts = predict_posts(user_id)
    
    # Print results
    print(json.dumps(recommended_posts, indent=2))