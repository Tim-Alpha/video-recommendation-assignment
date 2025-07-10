import os
from sqlalchemy.orm import Session
from app.database import engine, Base, SessionLocal
from app.models import User, Category, Topic, Post, UserInteraction

# Create tables if they don't exist
Base.metadata.create_all(bind=engine)

def seed_data():
    db: Session = SessionLocal()
    try:
        # Seed categories
        categories = [
            ("Education", "Educational videos", "https://example.com/edu.png"),
            ("Entertainment", "Fun videos", "https://example.com/ent.png"),
            ("Technology", "Tech and gadgets", "https://example.com/tech.png"),
            ("Music", "Music videos", "https://example.com/music.png"),
            ("Sports", "Sports highlights", "https://example.com/sports.png")
        ]
        cat_objs = {}
        for name, desc, img in categories:
            cat = db.query(Category).filter_by(name=name).first()
            if not cat:
                cat = Category(name=name, count=1, description=desc, image_url=img)
                db.add(cat)
                db.commit()
                print(f"Created category: {name}")
            cat_objs[name] = db.query(Category).filter_by(name=name).first()

        # Seed users
        users = [
            ("doey", "Doe", "Y", "Doe Y", "https://example.com/doe.png", "regular", False, False),
            ("janed", "Jane", "Doe", "Jane Doe", "https://example.com/jane.png", "regular", True, False),
            ("alicew", "Alice", "Wonder", "Alice Wonder", "https://example.com/alice.png", "admin", True, True),
            ("bobm", "Bob", "Marley", "Bob Marley", "https://example.com/bob.png", "regular", False, True)
        ]
        user_objs = {}
        for uname, fname, lname, name, pic, utype, evm, sol in users:
            user = db.query(User).filter_by(username=uname).first()
            if not user:
                user = User(username=uname, first_name=fname, last_name=lname, name=name, picture_url=pic, user_type=utype, has_evm_wallet=evm, has_solana_wallet=sol)
                db.add(user)
                db.commit()
                print(f"Created user: {uname}")
            user_objs[uname] = db.query(User).filter_by(username=uname).first()

        # Seed topics
        topics = [
            ("Python Basics", "Learn Python", "https://example.com/python.png", "python-basics", True, "EDU", 1, "en", user_objs["doey"].id),
            ("Comedy", "Comedy videos", "https://example.com/comedy.png", "comedy", True, "ENT", 1, "en", user_objs["janed"].id),
            ("AI Trends", "Latest in AI", "https://example.com/ai.png", "ai-trends", True, "TECH", 1, "en", user_objs["alicew"].id),
            ("Football", "Football highlights", "https://example.com/football.png", "football", True, "SPORTS", 1, "en", user_objs["bobm"].id),
            ("Guitar Lessons", "Learn guitar", "https://example.com/guitar.png", "guitar-lessons", True, "MUSIC", 1, "en", user_objs["alicew"].id)
        ]
        topic_objs = {}
        for name, desc, img, slug, pub, pcode, pcount, lang, owner_id in topics:
            topic = db.query(Topic).filter_by(slug=slug).first()
            if not topic:
                topic = Topic(name=name, description=desc, image_url=img, slug=slug, is_public=pub, project_code=pcode, posts_count=pcount, language=lang, owner_id=owner_id)
                db.add(topic)
                db.commit()
                print(f"Created topic: {name}")
            topic_objs[slug] = db.query(Topic).filter_by(slug=slug).first()

        # Seed posts
        posts = [
            ("Intro to Python", True, "intro-python", "vid001", "https://example.com/video.mp4", "https://example.com/thumb.png", user_objs["doey"].id, cat_objs["Education"].id, topic_objs["python-basics"].id),
            ("Funny Cats", True, "funny-cats", "vid002", "https://example.com/cat.mp4", "https://example.com/catthumb.png", user_objs["janed"].id, cat_objs["Entertainment"].id, topic_objs["comedy"].id),
            ("AI Revolution", True, "ai-revolution", "vid003", "https://example.com/ai.mp4", "https://example.com/aithumb.png", user_objs["alicew"].id, cat_objs["Technology"].id, topic_objs["ai-trends"].id),
            ("Champions League", True, "champions-league", "vid004", "https://example.com/football.mp4", "https://example.com/footballthumb.png", user_objs["bobm"].id, cat_objs["Sports"].id, topic_objs["football"].id),
            ("Guitar Solo", True, "guitar-solo", "vid005", "https://example.com/guitar.mp4", "https://example.com/guitarthumb.png", user_objs["alicew"].id, cat_objs["Music"].id, topic_objs["guitar-lessons"].id)
        ]
        post_objs = {}
        for title, avail, slug, ident, vlink, thumb, owner_id, cat_id, topic_id in posts:
            post = db.query(Post).filter_by(slug=slug).first()
            if not post:
                post = Post(title=title, is_available_in_public_feed=avail, slug=slug, identifier=ident, video_link=vlink, thumbnail_url=thumb, owner_id=owner_id, category_id=cat_id, topic_id=topic_id)
                db.add(post)
                db.commit()
                print(f"Created post: {title}")
            post_objs[slug] = db.query(Post).filter_by(slug=slug).first()

        # Seed user interactions
        interactions = [
            (user_objs["doey"].id, post_objs["intro-python"].id, "view"),
            (user_objs["janed"].id, post_objs["funny-cats"].id, "like"),
            (user_objs["alicew"].id, post_objs["ai-revolution"].id, "rate"),
            (user_objs["bobm"].id, post_objs["champions-league"].id, "bookmark"),
            (user_objs["alicew"].id, post_objs["guitar-solo"].id, "view"),
            (user_objs["doey"].id, post_objs["ai-revolution"].id, "like"),
            (user_objs["bobm"].id, post_objs["funny-cats"].id, "view")
        ]
        for uid, pid, itype in interactions:
            exists = db.query(UserInteraction).filter_by(user_id=uid, post_id=pid, interaction_type=itype).first()
            if not exists:
                interaction = UserInteraction(user_id=uid, post_id=pid, interaction_type=itype)
                db.add(interaction)
                db.commit()
                print(f"Created interaction: user {uid} {itype} post {pid}")
        print("Database seeded successfully with more diverse data.")
    finally:
        db.close()

if __name__ == "__main__":
    seed_data() 