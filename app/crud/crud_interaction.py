from sqlalchemy.orm import Session
from app.models.interaction import Interaction

def create_interaction(db: Session, user_id: int, post_id: int, interaction_type: str):
    db_interaction = Interaction(
        user_id=user_id,
        post_id=post_id,
        interaction_type=interaction_type
    )
    db.add(db_interaction)
    db.commit()
    db.refresh(db_interaction)
    return db_interaction

# We will need these functions for the recommendation logic later
def get_user_interaction_post_ids(db: Session, user_id: int):
    interactions = db.query(Interaction.post_id).filter(Interaction.user_id == user_id).distinct().all()
    return {interaction.post_id for interaction in interactions}

def get_user_liked_categories(db: Session, user_id: int):
    # Get project_codes from posts that the user has 'liked' or 'inspired'
    from app.models.post import Post
    categories = (
        db.query(Post.project_code)
        .join(Interaction, Post.id == Interaction.post_id)
        .filter(Interaction.user_id == user_id)
        .filter(Interaction.interaction_type.in_(['like', 'inspire']))
        .distinct()
        .all()
    )
    return [category.project_code for category in categories]