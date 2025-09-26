from sqlalchemy.orm import Session
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn.metrics.pairwise import cosine_similarity
import random
from app.data import SessionLocal
from app.models.model import User, Post, Interaction   


def get_posts_from_db():
    """Fetch all posts from DB."""
    db: Session = SessionLocal()
    try:
        return db.query(Post).all()
    finally:
        db.close()


def get_user_interactions(username: str):
    """Fetch posts that a user has interacted with (view/like/inspire/rating)."""
    db: Session = SessionLocal()
    try:
        user = db.query(User).filter(User.username == username).first()
        if not user:
            return [], None
        posts = [i.post for i in user.interactions]
        return posts, user
    finally:
        db.close()


def train_kmeans(posts, num_clusters=10):
    """Cluster posts using KMeans on post titles."""
    texts = [p.title or "" for p in posts]
    vectorizer = TfidfVectorizer(stop_words="english")
    X = vectorizer.fit_transform(texts)

    kmeans = KMeans(n_clusters=num_clusters, random_state=42, n_init="auto")
    kmeans.fit(X)
    return kmeans, vectorizer, X


def recommend_for_user(username: str, category: str = None, top_n: int = 10):
    """Generate recommendations for a user (with optional category filter)."""
    posts = get_posts_from_db()
    if not posts:
        return []


    kmeans, vectorizer, X = train_kmeans(posts)
    user_posts, user = get_user_interactions(username)

    if not user_posts:  
        if category:
            filtered = [p for p in posts if p.category and category.lower() in p.category.lower()]
            return random.sample(filtered, min(top_n, len(filtered))) if filtered else random.sample(posts, top_n)
        return random.sample(posts, top_n)
    user_texts = [p.title or "" for p in user_posts]
    user_vec = vectorizer.transform(user_texts).mean(axis=0)
    sims = cosine_similarity(user_vec, X).flatten()

    ranked_indices = sims.argsort()[::-1]

    recommendations = []
    for idx in ranked_indices:
        p = posts[idx]
        if p in user_posts:
            continue

        if category and (not p.category or category.lower() not in p.category.lower()):
            continue

        recommendations.append(p)
        if len(recommendations) >= top_n:
            break

    return recommendations


if __name__ == "__main__":
    username = "Anushka"
    category = None  
    recs = recommend_for_user(username, category)

    print(f"Found {len(recs)} recommendations for {username} (category={category})\n")
    for r in recs:
        print(f" Post ID: {r.post_id} | {r.title} | {r.category}")

