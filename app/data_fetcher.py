import random
from datetime import datetime
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app import models

# Interaction types
INTERACTION_TYPES = ["view", "like", "inspire", "rating"]

def generate_random_interactions():
    db: Session = SessionLocal()
    try:
        # Clear previous interactions for a fresh demo
        db.query(models.Interaction).delete()
        db.commit()

        users = db.query(models.User).all()
        videos = db.query(models.Video).all()

        for user in users:
            # Each user interacts with 2-5 videos randomly
            for _ in range(random.randint(2, 5)):
                video = random.choice(videos)
                interaction_type = random.choice(INTERACTION_TYPES)

                # Add new interaction
                interaction = models.Interaction(
                    user_id=user.id,
                    video_id=video.id,
                    interaction_type=interaction_type,
                    timestamp=datetime.utcnow()
                )
                db.add(interaction)
        db.commit()
        print("Random interactions generated successfully!")
    except Exception as e:
        db.rollback()
        print("Error generating interactions:", e)
    finally:
        db.close()


if __name__ == "__main__":
    generate_random_interactions()
