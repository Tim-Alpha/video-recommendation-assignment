from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import requests
import logging
from models import Base, User, Post, PostView, PostLike, PostInspire, PostRating, UpdatedPostSummary
import os

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Create SQLite database
engine = create_engine('sqlite:///data.db', echo=True)

# Create tables
Base.metadata.create_all(engine)

def fetch_post_likes_ids():
    """Fetch user_id and post_id for all post likes from the database."""
    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        likes = session.query(PostLike.user_id, PostLike.post_id).all()
        data = {
            "likes": [
                {
                    "user_id": like.user_id,
                    "post_id": like.post_id
                }
                for like in likes
            ]
        }
        return data
    finally:
        session.close()

def fetch_post_views_ids():
    """Fetch user_id and post_id for all post views from the database."""
    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        views = session.query(PostView.user_id, PostView.post_id).all()
        data = {
            "views": [
                {
                    "user_id": view.user_id,
                    "post_id": view.post_id
                }
                for view in views
            ]
        }
        return data
    finally:
        session.close()

def fetch_post_inspires_ids():
    """Fetch user_id and post_id for all post inspires from the database."""
    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        inspires = session.query(PostInspire.user_id, PostInspire.post_id).all()
        data = {
            "inspires": [
                {
                    "user_id": inspire.user_id,
                    "post_id": inspire.post_id
                }
                for inspire in inspires
            ]
        }
        return data
    finally:
        session.close()

def fetch_post_ratings_ids_and_rating():
    """Fetch user_id, post_id, and rating_percent for all post ratings from the database."""
    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        ratings = session.query(PostRating.user_id, PostRating.post_id, PostRating.rating_percent).all()
        data = {
            "ratings": [
                {
                    "user_id": rating.user_id,
                    "post_id": rating.post_id,
                    "rating_percent": float(rating.rating_percent) if rating.rating_percent else 0.0
                }
                for rating in ratings
            ]
        }
        return data
    finally:
        session.close()

def fetch_and_store_users(api_endpoint="http://localhost:8000/users/get_all"):
    """
    Fetch user data from API endpoint and store it in the database.
    Stops and raises an exception on the first failure.
    """
    logger.info(f"Fetching users from {api_endpoint}")
    try:
        response = requests.get(api_endpoint, timeout=100)
        response.raise_for_status()
        data = response.json()
    except requests.RequestException as e:
        logger.error(f"Failed to fetch users from API: {str(e)}")
        raise Exception(f"API request failed: {str(e)}")

    if 'users' not in data:
        logger.error("API response does not contain 'users' key")
        raise Exception("API response missing 'users' key")

    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        for i, user_data in enumerate(data['users']):
            logger.info(f"Processing user {i+1}: {user_data.get('username', 'unknown')}")
            # Convert last_login
            if user_data.get('last_login'):
                try:
                    user_data['last_login'] = datetime.strptime(
                        user_data['last_login'], "%Y-%m-%d %H:%M:%S"
                    )
                except ValueError as e:
                    logger.warning(f"Invalid last_login format for user {user_data.get('username')}: {str(e)}")
                    user_data['last_login'] = None
            else:
                user_data['last_login'] = None

            # Handle instagram_url
            try:
                user_data['instagram_url'] = user_data['instagram-url']
                del user_data['instagram-url']
            except KeyError as e:
                logger.error(f"Missing 'instagram-url' for user {user_data.get('username')}")
                raise Exception(f"KeyError in user data: {str(e)}")

            # Create and merge user
            try:
                user = User(**user_data)
                session.merge(user)
            except Exception as e:
                logger.error(f"Failed to create/merge user {user_data.get('username')}: {str(e)}")
                raise Exception(f"User creation failed: {str(e)}")

        # Commit transaction
        try:
            session.commit()
            logger.info(f"Successfully added/updated {len(data['users'])} users")
        except Exception as e:
            logger.error(f"Failed to commit users to database: {str(e)}")
            raise Exception(f"Database commit failed: {str(e)}")

    finally:
        session.close()
        logger.info("Database session closed")

def fetch_and_store_posts(api_endpoint="http://localhost:8000/posts/summary/get"):
    """
    Fetch post data from API endpoint and store it in the database.
    Stops and raises an exception on the first failure.
    """
    logger.info(f"Fetching posts from {api_endpoint}")
    try:
        response = requests.get(api_endpoint, timeout=100)
        response.raise_for_status()
        data = response.json()
    except requests.RequestException as e:
        logger.error(f"Failed to fetch posts from API: {str(e)}")
        raise Exception(f"API request failed: {str(e)}")

    if 'posts' not in data:
        logger.error("API response does not contain 'posts' key")
        raise Exception("API response missing 'posts' key")

    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        for i, post_data in enumerate(data['posts']):
            logger.info(f"Processing post {i+1}: {post_data.get('title', 'unknown')}")
            # Convert created_at
            if post_data.get('created_at'):
                try:
                    post_data['created_at'] = datetime.fromtimestamp(
                        post_data['created_at'] / 1000.0
                    )
                except (ValueError, TypeError) as e:
                    logger.warning(f"Invalid created_at for post {post_data.get('title')}: {str(e)}")
                    post_data['created_at'] = None
            else:
                post_data['created_at'] = None

            # Create and merge post
            try:
                post = Post(**post_data)
                session.merge(post)
            except Exception as e:
                logger.error(f"Failed to create/merge post {post_data.get('title')}: {str(e)}")
                raise Exception(f"Post creation failed: {str(e)}")

        # Commit transaction
        try:
            session.commit()
            logger.info(f"Successfully added/updated {len(data['posts'])} posts")
        except Exception as e:
            logger.error(f"Failed to commit posts to database: {str(e)}")
            raise Exception(f"Database commit failed: {str(e)}")

    finally:
        session.close()
        logger.info("Database session closed")

def fetch_and_store_post_views(api_endpoint="http://localhost:8000/posts/view"):
    """
    Fetch post view data from API endpoint and store it in the database.
    Stops and raises an exception on the first failure.
    """
    logger.info(f"Fetching post views from {api_endpoint}")
    try:
        response = requests.get(api_endpoint, timeout=100)
        response.raise_for_status()
        data = response.json()
    except requests.RequestException as e:
        logger.error(f"Failed to fetch post views from API: {str(e)}")
        raise Exception(f"API request failed: {str(e)}")

    if 'posts' not in data:
        logger.error("API response does not contain 'posts' key")
        raise Exception("API response missing 'posts' key")

    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        for i, view_data in enumerate(data['posts']):
            logger.info(f"Processing post view {i+1}: post_id {view_data.get('post_id')}")
            # Convert viewed_at
            if view_data.get('viewed_at'):
                try:
                    view_data['viewed_at'] = datetime.strptime(
                        view_data['viewed_at'], "%Y-%m-%d %H:%M:%S"
                    )
                except ValueError as e:
                    logger.warning(f"Invalid viewed_at format for post view {view_data.get('post_id')}: {str(e)}")
                    view_data['viewed_at'] = None
            else:
                view_data['viewed_at'] = None

            # Create and merge post view
            try:
                view = PostView(**view_data)
                session.merge(view)
            except Exception as e:
                logger.error(f"Failed to create/merge post view {view_data.get('post_id')}: {str(e)}")
                raise Exception(f"Post view creation failed: {str(e)}")

        # Commit transaction
        try:
            session.commit()
            logger.info(f"Successfully added/updated {len(data['posts'])} post views")
        except Exception as e:
            logger.error(f"Failed to commit post views to database: {str(e)}")
            raise Exception(f"Database commit failed: {str(e)}")

    finally:
        session.close()
        logger.info("Database session closed")

def fetch_and_store_post_likes(api_endpoint="http://localhost:8000/posts/like"):
    """
    Fetch post like data from API endpoint and store it in the database.
    Stops and raises an exception on the first failure.
    """
    logger.info(f"Fetching post likes from {api_endpoint}")
    try:
        response = requests.get(api_endpoint, timeout=100)
        response.raise_for_status()
        data = response.json()
    except requests.RequestException as e:
        logger.error(f"Failed to fetch post likes from API: {str(e)}")
        raise Exception(f"API request failed: {str(e)}")

    if 'posts' not in data:
        logger.error("API response does not contain 'posts' key")
        raise Exception("API response missing 'posts' key")

    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        for i, like_data in enumerate(data['posts']):
            logger.info(f"Processing post like {i+1}: post_id {like_data.get('post_id')}")
            # Convert liked_at
            if like_data.get('liked_at'):
                try:
                    like_data['liked_at'] = datetime.strptime(
                        like_data['liked_at'], "%Y-%m-%d %H:%M:%S"
                    )
                except ValueError as e:
                    logger.warning(f"Invalid liked_at format for post like {like_data.get('post_id')}: {str(e)}")
                    like_data['liked_at'] = None
            else:
                like_data['liked_at'] = None

            # Create and merge post like
            try:
                like = PostLike(**like_data)
                session.merge(like)
            except Exception as e:
                logger.error(f"Failed to create/merge post like {like_data.get('post_id')}: {str(e)}")
                raise Exception(f"Post like creation failed: {str(e)}")

        # Commit transaction
        try:
            session.commit()
            logger.info(f"Successfully added/updated {len(data['posts'])} post likes")
        except Exception as e:
            logger.error(f"Failed to commit post likes to database: {str(e)}")
            raise Exception(f"Database commit failed: {str(e)}")

    finally:
        session.close()
        logger.info("Database session closed")

def fetch_and_store_post_inspires(api_endpoint="http://localhost:8000/posts/inspire"):
    """
    Fetch post inspire data from API endpoint and store it in the database.
    Stops and raises an exception on the first failure.
    """
    logger.info(f"Fetching post inspires from {api_endpoint}")
    try:
        response = requests.get(api_endpoint, timeout=100)
        response.raise_for_status()
        data = response.json()
    except requests.RequestException as e:
        logger.error(f"Failed to fetch post inspires from API: {str(e)}")
        raise Exception(f"API request failed: {str(e)}")

    if 'posts' not in data:
        logger.error("API response does not contain 'posts' key")
        raise Exception("API response missing 'posts' key")

    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        for i, inspire_data in enumerate(data['posts']):
            logger.info(f"Processing post inspire {i+1}: post_id {inspire_data.get('post_id')}")
            # Convert inspired_at
            if inspire_data.get('inspired_at'):
                try:
                    inspire_data['inspired_at'] = datetime.strptime(
                        inspire_data['inspired_at'], "%Y-%m-%d %H:%M:%S"
                    )
                except ValueError as e:
                    logger.warning(f"Invalid inspired_at format for post inspire {inspire_data.get('post_id')}: {str(e)}")
                    inspire_data['inspired_at'] = None
            else:
                inspire_data['inspired_at'] = None

            # Create and merge post inspire
            try:
                inspire = PostInspire(**inspire_data)
                session.merge(inspire)
            except Exception as e:
                logger.error(f"Failed to create/merge post inspire {inspire_data.get('post_id')}: {str(e)}")
                raise Exception(f"Post inspire creation failed: {str(e)}")

        # Commit transaction
        try:
            session.commit()
            logger.info(f"Successfully added/updated {len(data['posts'])} post inspires")
        except Exception as e:
            logger.error(f"Failed to commit post inspires to database: {str(e)}")
            raise Exception(f"Database commit failed: {str(e)}")

    finally:
        session.close()
        logger.info("Database session closed")

def fetch_and_store_post_ratings(api_endpoint="http://localhost:8000/posts/rating"):
    """
    Fetch post rating data from API endpoint and store it in the database.
    Stops and raises an exception on the first failure.
    """
    logger.info(f"Fetching post ratings from {api_endpoint}")
    try:
        response = requests.get(api_endpoint, timeout=100)
        response.raise_for_status()
        data = response.json()
    except requests.RequestException as e:
        logger.error(f"Failed to fetch post ratings from API: {str(e)}")
        raise Exception(f"API request failed: {str(e)}")

    if 'posts' not in data:
        logger.error("API response does not contain 'posts' key")
        raise Exception("API response missing 'posts' key")

    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        for i, rating_data in enumerate(data['posts']):
            logger.info(f"Processing post rating {i+1}: post_id {rating_data.get('post_id')}")
            # Convert rated_at
            if rating_data.get('rated_at'):
                try:
                    rating_data['rated_at'] = datetime.strptime(
                        rating_data['rated_at'], "%Y-%m-%d %H:%M:%S"
                    )
                except ValueError as e:
                    logger.warning(f"Invalid rated_at format for post rating {rating_data.get('post_id')}: {str(e)}")
                    rating_data['rated_at'] = None
            else:
                rating_data['rated_at'] = None

            # Create and merge post rating
            try:
                rating = PostRating(**rating_data)
                session.merge(rating)
            except Exception as e:
                logger.error(f"Failed to create/merge post rating {rating_data.get('post_id')}: {str(e)}")
                raise Exception(f"Post rating creation failed: {str(e)}")

        # Commit transaction
        try:
            session.commit()
            logger.info(f"Successfully added/updated {len(data['posts'])} post ratings")
        except Exception as e:
            logger.error(f"Failed to commit post ratings to database: {str(e)}")
            raise Exception(f"Database commit failed: {str(e)}")

    finally:
        session.close()
        logger.info("Database session closed")


def load_post_ratings():
    """Load post ratings from database and return in specified format."""
    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        ratings = session.query(PostRating).all()
        data = {
            "posts": [
                {
                    "id": r.id,
                    "post_id": r.post_id,
                    "user_id": r.user_id,
                    "rating_percent": r.rating_percent,
                    "rated_at": r.rated_at.strftime("%Y-%m-%d %H:%M:%S") if r.rated_at else None
                }
                for r in ratings
            ]
        }
        return data
    finally:
        session.close()


def load_post_inspires():
    """Load post inspires from database and return in specified format."""
    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        inspires = session.query(PostInspire).all()
        data = {
            "posts": [
                {
                    "id": i.id,
                    "post_id": i.post_id,
                    "user_id": i.user_id,
                    "inspired_at": i.inspired_at.strftime("%Y-%m-%d %H:%M:%S") if i.inspired_at else None
                }
                for i in inspires
            ]
        }
        return data
    finally:
        session.close()


def load_post_likes():
    """Load post likes from database and return in specified format."""
    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        likes = session.query(PostLike).all()
        data = {
            "posts": [
                {
                    "id": l.id,
                    "post_id": l.post_id,
                    "user_id": l.user_id,
                    "liked_at": l.liked_at.strftime("%Y-%m-%d %H:%M:%S") if l.liked_at else None
                }
                for l in likes
            ]
        }
        return data
    finally:
        session.close()


def load_post_views():
    """Load post views from database and return in specified format."""
    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        views = session.query(PostView).all()
        data = {
            "posts": [
                {
                    "id": v.id,
                    "post_id": v.post_id,
                    "user_id": v.user_id,
                    "viewed_at": v.viewed_at.strftime("%Y-%m-%d %H:%M:%S") if v.viewed_at else None
                }
                for v in views
            ]
        }
        return data
    finally:
        session.close()

def load_all_posts():
    """Load all posts from database and return in specified format."""
    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        posts = session.query(Post).all()
        data = {
            "posts": [
                {
                    "id": p.id,
                    "category": p.category,
                    "topic": p.topic,
                    "slug": p.slug,
                    "title": p.title,
                    "identifier": p.identifier,
                    "comment_count": p.comment_count,
                    "upvote_count": p.upvote_count,
                    "view_count": p.view_count,
                    "exit_count": p.exit_count,
                    "rating_count": p.rating_count,
                    "average_rating": p.average_rating,
                    "share_count": p.share_count,
                    "bookmark_count": p.bookmark_count,
                    "video_link": p.video_link,
                    "contract_address": p.contract_address,
                    "chain_id": p.chain_id,
                    "chart_url": p.chart_url,
                    "baseToken": p.baseToken,
                    "is_locked": p.is_locked,
                    "created_at": p.created_at.strftime("%Y-%m-%d %H:%M:%S") if p.created_at else None,
                    "first_name": p.first_name,
                    "last_name": p.last_name,
                    "username": p.username,
                    "user_type": p.user_type,
                    "has_evm_wallet": p.has_evm_wallet,
                    "has_solana_wallet": p.has_solana_wallet,
                    "is_viewed": p.is_viewed,
                    "upvoted": p.upvoted,
                    "bookmarked": p.bookmarked,
                    "is_available_in_public_feed": p.is_available_in_public_feed,
                    "thumbnail_url": p.thumbnail_url,
                    "gif_thumbnail_url": p.gif_thumbnail_url,
                    "following": p.following,
                    "picture_url": p.picture_url,
                    "post_summary": p.post_summary,
                    "tags": p.tags,
                    "source_matrix": p.source_matrix,
                }
                for p in posts
            ]
        }
        return data
    finally:
        session.close()

def store_updated_post_summaries(updated_posts):
    """
    Store updated post summaries in the updated_post_summaries table.
    Stops and raises an exception on the first failure.
    
    Args:
        updated_posts (List[Dict]): List of dictionaries containing updated post data.
    """
    logger.info("Storing updated post summaries in the database")
    
    if not updated_posts:
        logger.warning("No updated posts provided to store")
        return

    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        for i, post_data in enumerate(updated_posts):
            logger.info(f"Processing updated post summary {i+1}: post_id {post_data.get('id')}")
            
            # Validate required fields
            required_fields = ['id', 'username', 'summary', 'category']
            for field in required_fields:
                if field not in post_data or post_data[field] is None:
                    logger.error(f"Missing or null required field '{field}' for post {post_data.get('id')}")
                    raise Exception(f"Missing required field: {field}")

            # Create dictionary for UpdatedPostSummary
            summary_data = {
                'post_id': post_data.get('id'),
                'upvote_count': post_data.get('upvote_count', 0),
                'view_count': post_data.get('view_count', 0),
                'average_rating': post_data.get('average_rating', 0.0),
                'username': post_data.get('username'),
                'keywords': post_data.get('keywords', []),
                'no_of_person_in_video': post_data.get('no_of_person_in_video', 0),
                'estimated_duration': post_data.get('estimated_duration', ''),
                'main_character_gender': post_data.get('main_character_gender', ''),
                'summary': post_data.get('summary'),
                'category': post_data.get('category')
            }

            # Create and merge summary
            try:
                summary = UpdatedPostSummary(**summary_data)
                session.merge(summary)
            except Exception as e:
                logger.error(f"Failed to create/merge updated post summary for post_id {post_data.get('id')}: {str(e)}")
                raise Exception(f"Updated post summary creation failed: {str(e)}")

        # Commit transaction
        try:
            session.commit()
            logger.info(f"Successfully added/updated {len(updated_posts)} post summaries")
        except Exception as e:
            logger.error(f"Failed to commit updated post summaries to database: {str(e)}")
            raise Exception(f"Database commit failed: {str(e)}")

    finally:
        session.close()
        logger.info("Database session closed")

def load_updated_post_summaries():
    """Load all updated post summaries from database and return in specified format."""
    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        summaries = session.query(UpdatedPostSummary).all()
        data = {
            "posts": [
                {
                    "post_id": s.post_id,
                    "upvote_count": s.upvote_count,
                    "view_count": s.view_count,
                    "average_rating": float(s.average_rating) if s.average_rating else 0.0,
                    "username": s.username,
                    "keywords": s.keywords,
                    "no_of_person_in_video": s.no_of_person_in_video,
                    "estimated_duration": s.estimated_duration,
                    "main_character_gender": s.main_character_gender,
                    "summary": s.summary,
                    "category": s.category
                }
                for s in summaries
            ]
        }
        return data
    finally:
        session.close()


def create_db():
    """
    Check if database exists and has data. If not, run the main data fetching functions.
    """
    db_path = 'data.db'
    if not os.path.exists(db_path):
        logger.info("Database does not exist. Creating and populating database.")
        try:
            fetch_and_store_users()
            fetch_and_store_posts()
            fetch_and_store_post_views()
            fetch_and_store_post_likes()
            fetch_and_store_post_inspires()
            fetch_and_store_post_ratings()
        except Exception as e:
            logger.error(f"Failed to populate database: {str(e)}")
            raise
    else:
        Session = sessionmaker(bind=engine)
        session = Session()
        try:
            user_count = session.query(User).count()
            if user_count == 0:
                logger.info("Database exists but contains no users. Populating database.")
                try:
                    fetch_and_store_users()
                    fetch_and_store_posts()
                    fetch_and_store_post_views()
                    fetch_and_store_post_likes()
                    fetch_and_store_post_inspires()
                    fetch_and_store_post_ratings()
                except Exception as e:
                    logger.error(f"Failed to populate database: {str(e)}")
                    raise
            else:
                logger.info("Database exists and contains data. Skipping population.")
        finally:
            session.close()
            logger.info("Database session closed")

if __name__ == "__main__":
    try:
        create_db()
    except Exception as e:
        logger.error(f"Program stopped due to error: {str(e)}")
        raise