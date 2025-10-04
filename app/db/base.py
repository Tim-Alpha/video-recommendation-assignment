# File: app/db/base.py

# Import the Base class from where it is defined.
from app.db.base_class import Base

# Import all the models to register them with the metadata.
from app.models.user import User
from app.models.post import Post
from app.models.interaction import Interaction