from app.data import SessionLocal
from app.models import model

def check_data():
    db = SessionLocal()
    try:
        users = db.query(model.User).all()
        posts = db.query(model.Post).all()
        interactions = db.query(model.Interaction).all()

        print("--- USERS ---")
        for u in users:
            print(f"{u.username} | {u.email}")
        print(f"Total users records: {len(users)}\n")

        print("--- POSTS ---")
        for p in posts:
            print(f"{p.post_id} | {p.title}")
        print(f"Total post records: {len(posts)}\n")

        print("--- INTERACTIONS ---")
        for i in interactions:
            print(f"{i.user_id} | {i.post_id} | {i.type}")
        print(f"Total interaction records: {len(interactions)}\n")

    finally:
        db.close()

if __name__ == "__main__":
    check_data()
