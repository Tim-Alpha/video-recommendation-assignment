from sqlalchemy.orm import Session
from app.database import SessionLocal, engine
from app import models
from datetime import datetime
import random

# Drop and create tables (optional, for fresh start)
models.Base.metadata.drop_all(bind=engine)
models.Base.metadata.create_all(bind=engine)

# Mock users
USERS = [
    {"username": "John"},
    {"username": "Alice"},
    {"username": "Bob"},
]

# Mock videos
VIDEOS = [
    {"title": "Motivational Video 1", "category": "Motivation"},
    {"title": "Motivational Video 2", "category": "Motivation"},
    {"title": "Wellness Video", "category": "Wellness"},
    {"title": "Fitness Tips", "category": "Health"},
    {"title": "Meditation Guide", "category": "Wellness"},
    {"title": "Career Advice", "category": "Motivation"},
]

# Mock interactions (randomly generate some interactions)
INTERACTION_TYPES = ["view", "like", "inspire", "rating"]

def populate_mock_data():
    db: Session = SessionLocal()
    try:
        # Add users
        user_objs = []
        for u in USERS:
            user_obj = models.User(username=u["username"])
            db.add(user_obj)
            user_objs.append(user_obj)
        db.commit()

        # Add videos
        video_objs = []
        for v in VIDEOS:
            video_obj = models.Video(title=v["title"], category=v["category"])
            db.add(video_obj)
            video_objs.append(video_obj)
        db.commit()

        # Add random interactions for each user
        for user in user_objs:
            for _ in range(random.randint(2, 5)):  # 2-5 interactions per user
                video = random.choice(video_objs)
                interaction_type = random.choice(INTERACTION_TYPES)
                interaction = models.Interaction(
                    user_id=user.id,
                    video_id=video.id,
                    interaction_type=interaction_type,
                    timestamp=datetime.utcnow()
                )
                db.add(interaction)
        db.commit()

        print("Mock data populated successfully!")

    except Exception as e:
        db.rollback()
        print("Error populating mock data:", e)
    finally:
        db.close()


if __name__ == "__main__":
    populate_mock_data()
