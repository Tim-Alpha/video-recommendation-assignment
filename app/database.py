# app/database.py
from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
DATABASE_NAME = os.getenv("DATABASE_NAME", "video_recommendation")

client = MongoClient(MONGO_URI)
db = client[DATABASE_NAME]

# Collections
users_collection = db["users"]
feed_items_collection = db["feed_items"]
