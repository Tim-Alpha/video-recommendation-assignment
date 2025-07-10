from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.models import User, Post, UserInteraction, Category, Topic
from app.external_api import external_api
from app.recommendation_engine import recommendation_engine
import asyncio
from datetime import datetime
import json
import logging


class DataService:
    def __init__(self):
        self.last_sync_time = None
    
    async def sync_external_data(self, db: Session) -> Dict[str, Any]:
        """Sync data from external API to local database"""
        try:
            # Fetch all data from external API
            external_data = await external_api.fetch_all_data()
            
            sync_results = {
                "users_synced": 0,
                "posts_synced": 0,
                "interactions_synced": 0,
                "errors": []
            }
            
            # Sync users
            if external_data.get("users", {}).get("status"):
                users_data = external_data["users"].get("users", [])
                sync_results["users_synced"] = await self._sync_users(db, users_data)
            
            # Sync posts
            if external_data.get("posts", {}).get("status"):
                posts_data = external_data["posts"].get("post", [])
                sync_results["posts_synced"] = await self._sync_posts(db, posts_data)
            
            # Sync interactions
            sync_results["interactions_synced"] = await self._sync_interactions(db, external_data)
            
            self.last_sync_time = datetime.now()
            return sync_results
            
        except Exception as e:
            return {"error": str(e)}
    
    async def _sync_users(self, db: Session, users_data: List[Dict]) -> int:
        """Sync users from external API"""
        synced_count = 0
        
        for user_data in users_data:
            try:
                # Check if user exists
                existing_user = db.query(User).filter(
                    User.username == user_data.get("username")
                ).first()
                
                if existing_user:
                    # Update existing user
                    existing_user.first_name = user_data.get("first_name", "")
                    existing_user.last_name = user_data.get("last_name", "")
                    existing_user.name = user_data.get("name", "")
                    existing_user.picture_url = user_data.get("picture_url", "")
                    existing_user.user_type = user_data.get("user_type")
                    existing_user.has_evm_wallet = user_data.get("has_evm_wallet", False)
                    existing_user.has_solana_wallet = user_data.get("has_solana_wallet", False)
                else:
                    # Create new user
                    new_user = User(
                        username=user_data.get("username"),
                        first_name=user_data.get("first_name", ""),
                        last_name=user_data.get("last_name", ""),
                        name=user_data.get("name", ""),
                        picture_url=user_data.get("picture_url", ""),
                        user_type=user_data.get("user_type"),
                        has_evm_wallet=user_data.get("has_evm_wallet", False),
                        has_solana_wallet=user_data.get("has_solana_wallet", False)
                    )
                    db.add(new_user)
                
                synced_count += 1
                
            except Exception as e:
                logging.error(f"Error syncing user {user_data.get('username')}: {e}")
                continue
        
        db.commit()
        return synced_count
    
    async def _sync_posts(self, db: Session, posts_data: List[Dict]) -> int:
        """Sync posts from external API"""
        synced_count = 0
        
        for post_data in posts_data:
            try:
                # Check if post exists
                existing_post = db.query(Post).filter(
                    Post.identifier == post_data.get("identifier")
                ).first()
                
                # Sync owner
                owner_data = post_data.get("owner", {})
                owner = None
                if owner_data.get("username"):
                    owner = db.query(User).filter(
                        User.username == owner_data["username"]
                    ).first()
                
                # Sync category
                category_data = post_data.get("category", {})
                category = None
                if category_data.get("id"):
                    category = db.query(Category).filter(
                        Category.id == category_data["id"]
                    ).first()
                    
                    if not category and category_data.get("name"):
                        category = Category(
                            id=category_data["id"],
                            name=category_data["name"],
                            count=category_data.get("count", 0),
                            description=category_data.get("description", ""),
                            image_url=category_data.get("image_url", "")
                        )
                        db.add(category)
                
                # Sync topic
                topic_data = post_data.get("topic", {})
                topic = None
                if topic_data.get("id"):
                    topic = db.query(Topic).filter(
                        Topic.id == topic_data["id"]
                    ).first()
                    
                    if not topic and topic_data.get("name"):
                        topic_owner = None
                        if topic_data.get("owner", {}).get("username"):
                            topic_owner = db.query(User).filter(
                                User.username == topic_data["owner"]["username"]
                            ).first()
                        
                        topic = Topic(
                            id=topic_data["id"],
                            name=topic_data["name"],
                            description=topic_data.get("description", ""),
                            image_url=topic_data.get("image_url", ""),
                            slug=topic_data.get("slug", ""),
                            is_public=topic_data.get("is_public", True),
                            project_code=topic_data.get("project_code", ""),
                            posts_count=topic_data.get("posts_count", 0),
                            language=topic_data.get("language"),
                            owner_id=topic_owner.id if topic_owner else None
                        )
                        db.add(topic)
                
                if existing_post:
                    # Update existing post
                    existing_post.title = post_data.get("title", "")
                    existing_post.is_available_in_public_feed = post_data.get("is_available_in_public_feed", True)
                    existing_post.is_locked = post_data.get("is_locked", False)
                    existing_post.comment_count = post_data.get("comment_count", 0)
                    existing_post.upvote_count = post_data.get("upvote_count", 0)
                    existing_post.view_count = post_data.get("view_count", 0)
                    existing_post.exit_count = post_data.get("exit_count", 0)
                    existing_post.rating_count = post_data.get("rating_count", 0)
                    existing_post.average_rating = post_data.get("average_rating", 0)
                    existing_post.share_count = post_data.get("share_count", 0)
                    existing_post.bookmark_count = post_data.get("bookmark_count", 0)
                    existing_post.video_link = post_data.get("video_link", "")
                    existing_post.thumbnail_url = post_data.get("thumbnail_url", "")
                    existing_post.gif_thumbnail_url = post_data.get("gif_thumbnail_url", "")
                    existing_post.contract_address = post_data.get("contract_address", "")
                    existing_post.chain_id = post_data.get("chain_id", "")
                    existing_post.chart_url = post_data.get("chart_url", "")
                    existing_post.base_token_data = post_data.get("baseToken", {})
                    existing_post.tags = post_data.get("tags", [])
                    existing_post.owner_id = owner.id if owner else None
                    existing_post.category_id = category.id if category else None
                    existing_post.topic_id = topic.id if topic else None
                else:
                    # Create new post
                    new_post = Post(
                        identifier=post_data.get("identifier"),
                        title=post_data.get("title", ""),
                        slug=post_data.get("slug", ""),
                        is_available_in_public_feed=post_data.get("is_available_in_public_feed", True),
                        is_locked=post_data.get("is_locked", False),
                        comment_count=post_data.get("comment_count", 0),
                        upvote_count=post_data.get("upvote_count", 0),
                        view_count=post_data.get("view_count", 0),
                        exit_count=post_data.get("exit_count", 0),
                        rating_count=post_data.get("rating_count", 0),
                        average_rating=post_data.get("average_rating", 0),
                        share_count=post_data.get("share_count", 0),
                        bookmark_count=post_data.get("bookmark_count", 0),
                        video_link=post_data.get("video_link", ""),
                        thumbnail_url=post_data.get("thumbnail_url", ""),
                        gif_thumbnail_url=post_data.get("gif_thumbnail_url", ""),
                        contract_address=post_data.get("contract_address", ""),
                        chain_id=post_data.get("chain_id", ""),
                        chart_url=post_data.get("chart_url", ""),
                        base_token_data=post_data.get("baseToken", {}),
                        tags=post_data.get("tags", []),
                        owner_id=owner.id if owner else None,
                        category_id=category.id if category else None,
                        topic_id=topic.id if topic else None
                    )
                    db.add(new_post)
                
                synced_count += 1
                
            except Exception as e:
                logging.error(f"Error syncing post {post_data.get('identifier')}: {e}")
                continue
        
        db.commit()
        return synced_count
    
    async def _sync_interactions(self, db: Session, external_data: Dict) -> int:
        """Sync user interactions from external API"""
        synced_count = 0
        
        # Sync viewed posts
        if external_data.get("viewed_posts", {}).get("status"):
            viewed_data = external_data["viewed_posts"].get("post", [])
            synced_count += await self._sync_interaction_type(db, viewed_data, "view")
        
        # Sync liked posts
        if external_data.get("liked_posts", {}).get("status"):
            liked_data = external_data["liked_posts"].get("post", [])
            synced_count += await self._sync_interaction_type(db, liked_data, "like")
        
        # Sync inspired posts
        if external_data.get("inspired_posts", {}).get("status"):
            inspired_data = external_data["inspired_posts"].get("post", [])
            synced_count += await self._sync_interaction_type(db, inspired_data, "inspire")
        
        # Sync rated posts
        if external_data.get("rated_posts", {}).get("status"):
            rated_data = external_data["rated_posts"].get("post", [])
            synced_count += await self._sync_interaction_type(db, rated_data, "rate")
        
        return synced_count
    
    async def _sync_interaction_type(self, db: Session, posts_data: List[Dict], interaction_type: str) -> int:
        """Sync specific type of interactions"""
        synced_count = 0
        
        for post_data in posts_data:
            try:
                # Find post
                post = db.query(Post).filter(
                    Post.identifier == post_data.get("identifier")
                ).first()
                
                if not post:
                    continue
                
                # Find user (assuming we have user context)
                # For now, we'll create interactions without specific user
                # In a real scenario, you'd need to map interactions to users
                
                # Check if interaction already exists
                existing_interaction = db.query(UserInteraction).filter(
                    UserInteraction.post_id == post.id,
                    UserInteraction.interaction_type == interaction_type
                ).first()
                
                if not existing_interaction:
                    # Create new interaction
                    new_interaction = UserInteraction(
                        post_id=post.id,
                        interaction_type=interaction_type,
                        rating_value=post_data.get("average_rating") if interaction_type == "rate" else None
                    )
                    db.add(new_interaction)
                    synced_count += 1
                
            except Exception as e:
                logging.error(f"Error syncing {interaction_type} interaction: {e}")
                continue
        
        db.commit()
        return synced_count


class RecommendationService:
    def __init__(self):
        self.engine = recommendation_engine
    
    def get_personalized_feed(self, db: Session, username: str, limit: int = 10) -> List[Dict]:
        """Get personalized feed for a user"""
        try:
            # Check if user exists
            user = db.query(User).filter(User.username == username).first()
            if not user:
                # Return cold start recommendations
                posts = self.engine.get_cold_start_recommendations(db, limit)
            else:
                # Get personalized recommendations
                posts = self.engine.get_personalized_recommendations(db, username, limit)
            result = self._format_posts_response(posts)
            return result
        except Exception as e:
            logging.error(f"Error getting personalized feed: {e}")
            return []
    
    def get_category_feed(self, db: Session, username: str, project_code: str, limit: int = 10) -> List[Dict]:
        """Get category-specific feed for a user"""
        try:
            posts = self.engine.get_category_recommendations(db, username, project_code, limit)
            result = self._format_posts_response(posts)
            return result
        except Exception as e:
            logging.error(f"Error getting category feed: {e}")
            return []
    
    def _format_posts_response(self, posts: List[Post]) -> List[Dict]:
        """Format posts for API response"""
        formatted_posts = []
        
        for post in posts:
            formatted_post = {
                "id": post.id,
                "owner": {
                    "first_name": post.owner.first_name if post.owner else "",
                    "last_name": post.owner.last_name if post.owner else "",
                    "name": post.owner.name if post.owner else "",
                    "username": post.owner.username if post.owner else "",
                    "picture_url": post.owner.picture_url if post.owner else "",
                    "user_type": post.owner.user_type if post.owner else None,
                    "has_evm_wallet": post.owner.has_evm_wallet if post.owner else False,
                    "has_solana_wallet": post.owner.has_solana_wallet if post.owner else False
                },
                "category": {
                    "id": post.category.id if post.category else None,
                    "name": post.category.name if post.category else "",
                    "count": post.category.count if post.category else 0,
                    "description": post.category.description if post.category else "",
                    "image_url": post.category.image_url if post.category else ""
                },
                "topic": {
                    "id": post.topic.id if post.topic else None,
                    "name": post.topic.name if post.topic else "",
                    "description": post.topic.description if post.topic else "",
                    "image_url": post.topic.image_url if post.topic else "",
                    "slug": post.topic.slug if post.topic else "",
                    "is_public": post.topic.is_public if post.topic else True,
                    "project_code": post.topic.project_code if post.topic else "",
                    "posts_count": post.topic.posts_count if post.topic else 0,
                    "language": post.topic.language if post.topic else None,
                    "created_at": post.topic.created_at.isoformat() if post.topic and post.topic.created_at else None,
                    "owner": {
                        "first_name": post.topic.owner.first_name if post.topic and post.topic.owner else "",
                        "last_name": post.topic.owner.last_name if post.topic and post.topic.owner else "",
                        "name": post.topic.owner.name if post.topic and post.topic.owner else "",
                        "username": post.topic.owner.username if post.topic and post.topic.owner else "",
                        "profile_url": post.topic.owner.picture_url if post.topic and post.topic.owner else "",
                        "user_type": post.topic.owner.user_type if post.topic and post.topic.owner else None,
                        "has_evm_wallet": post.topic.owner.has_evm_wallet if post.topic and post.topic.owner else False,
                        "has_solana_wallet": post.topic.owner.has_solana_wallet if post.topic and post.topic.owner else False
                    }
                },
                "title": post.title,
                "is_available_in_public_feed": post.is_available_in_public_feed,
                "is_locked": post.is_locked,
                "slug": post.slug,
                "upvoted": False,  # Would need user context to determine
                "bookmarked": False,  # Would need user context to determine
                "following": False,  # Would need user context to determine
                "identifier": post.identifier,
                "comment_count": post.comment_count,
                "upvote_count": post.upvote_count,
                "view_count": post.view_count,
                "exit_count": post.exit_count,
                "rating_count": post.rating_count,
                "average_rating": post.average_rating,
                "share_count": post.share_count,
                "bookmark_count": post.bookmark_count,
                "video_link": post.video_link,
                "thumbnail_url": post.thumbnail_url,
                "gif_thumbnail_url": post.gif_thumbnail_url,
                "contract_address": post.contract_address or "",
                "chain_id": post.chain_id or "",
                "chart_url": post.chart_url or "",
                "baseToken": post.base_token_data or {
                    "address": "",
                    "name": "",
                    "symbol": "",
                    "image_url": ""
                },
                "created_at": int(post.created_at.timestamp() * 1000) if post.created_at else None,
                "tags": post.tags or []
            }
            
            formatted_posts.append(formatted_post)
        
        return formatted_posts


# Create global instances
data_service = DataService()
recommendation_service = RecommendationService() 