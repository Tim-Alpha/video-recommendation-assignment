from sqlalchemy import create_engine
import os

# Create the engine
engine = create_engine("sqlite:///socialverse.db")

# Extract and print the absolute path
db_path = engine.url.database
abs_db_path = os.path.abspath(db_path)

print("SQLite DB absolute path:", abs_db_path)
