from sqlalchemy.orm import Session
from app.models.post import Post
from app.schemas.post import PostCreate

def get_post_by_post_id(db: Session, post_id: str):
    return db.query(Post).filter(Post.post_id == post_id).first()

def create_post(db: Session, post: PostCreate):
    db_post = Post(
        post_id=post.post_id,
        project_code=post.project_code,
        content=post.content,
        thumbnail_url=post.thumbnail_url,
        video_link=post.video_link
    )
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    return db_post

def get_popular_posts(db: Session, limit: int = 20):
    return db.query(Post).order_by(Post.created_at.desc()).limit(limit).all()

def get_posts_by_category(db: Session, category_code: str, limit: int = 50):
    return db.query(Post).filter(Post.project_code == category_code).order_by(Post.created_at.desc()).limit(limit).all()