import requests
import sqlite3
import json
import os
import time
import sys
import subprocess
from datetime import datetime
import logging
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple, Union
from tqdm import tqdm
from neo4j import GraphDatabase

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("data_pipeline.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class Config:
    # Base API URLs (no query params)
    VIEWED_POSTS_URL = "https://api.socialverseapp.com/posts/view"
    LIKED_POSTS_URL = "https://api.socialverseapp.com/posts/like"
    INSPIRED_POSTS_URL = "https://api.socialverseapp.com/posts/inspire"
    RATED_POSTS_URL = "https://api.socialverseapp.com/posts/rating"
    ALL_POSTS_URL = "https://api.socialverseapp.com/posts/summary/get"
    ALL_USERS_URL = "https://api.socialverseapp.com/users/get_all"

    # API parameters
    DEFAULT_PARAMS = {
        "page": 1,
        "page_size": 1000,
        "resonance_algorithm": "resonance_algorithm_cjsvervb7dbhss8bdrj89s44jfjdbsjd0xnjkbvuire8zcjwerui3njfbvsujc5if"
    }

    # Authentication
    FLIC_TOKEN = "flic_11d3da28e403d182c36a3530453e290add87d0b4a40ee50f17611f180d47956f"
    HEADERS = {
        "Flic-Token": FLIC_TOKEN
    }

    # Database
    SQLITE_DB_PATH = "socialverse.db"

    # Other settings
    REQUEST_TIMEOUT = 120  # seconds
    RETRY_COUNT = 3
    RETRY_DELAY = 5  # seconds


# API Handler
class APIHandler:
    """Handles API requests and responses"""

    def __init__(self, config):
        self.config = config

    def make_request(self, url, params=None, use_headers=True):
        """Make an API request with retries"""
        if params is None:
            params = self.config.DEFAULT_PARAMS

        for attempt in range(self.config.RETRY_COUNT):
            try:
                logger.info(f"Making request to {url} with params={params}")
                response = requests.get(
                    url,
                    params=params,
                    headers=self.config.HEADERS if use_headers else None,
                    timeout=self.config.REQUEST_TIMEOUT
                )
                response.raise_for_status()
                return response.json()
            except requests.exceptions.RequestException as e:
                logger.error(f"Request failed (attempt {attempt+1}/{self.config.RETRY_COUNT}): {str(e)}")
                if attempt < self.config.RETRY_COUNT - 1:
                    logger.info(f"Retrying in {self.config.RETRY_DELAY} seconds...")
                    time.sleep(self.config.RETRY_DELAY)
                else:
                    logger.error(f"Max retries reached, giving up on {url}")
                    raise

    def fetch_paginated_data(self, url, use_headers=True):
        """Fetch data from all pages"""
        page = 1
        all_data = []

        while True:
            params = dict(self.config.DEFAULT_PARAMS, page=page)
            logger.info(f"Fetching page {page} from {url}")
            try:
                response = self.make_request(url, params=params, use_headers=use_headers)

                # Try different possible keys where data might be stored
                if isinstance(response, list):
                    page_data = response
                else:
                    page_data = response.get("data") or response.get("posts") or []

                if not page_data:
                    logger.info(f"No data found on page {page}")
                    break

                all_data.extend(page_data)
                page += 1
            except Exception as e:
                logger.error(f"Error fetching page {page} from {url}: {str(e)}")
                break

        return all_data

    def fetch_all_data(self):
        """Fetch all data from all endpoints"""
        data = {}

        endpoints = {
            "viewed_posts": self.config.VIEWED_POSTS_URL,
            "liked_posts": self.config.LIKED_POSTS_URL,
            "inspired_posts": self.config.INSPIRED_POSTS_URL,
            "rated_posts": self.config.RATED_POSTS_URL,
            "all_posts": self.config.ALL_POSTS_URL,
            "all_users": self.config.ALL_USERS_URL
        }

        for name, url in endpoints.items():
            try:
                logger.info(f"Fetching {name}")
                data[name] = self.fetch_paginated_data(url, use_headers=True)
            except Exception as e:
                logger.error(f"Failed to fetch {name}: {str(e)}")
                data[name] = {"status": "error", "message": str(e)}

        return data


class SQLiteHandler:
    """Handles SQLite database operations"""
    
    def __init__(self, config):
        self.config = config
        self.conn = None
        self.initialize_db()
        
    def initialize_db(self):
        """Initialize SQLite database and create tables if they don't exist"""
        try:
            logger.info(f"Initializing SQLite database at {self.config.SQLITE_DB_PATH}")
            self.conn = sqlite3.connect(self.config.SQLITE_DB_PATH)
            
            # Create tables
            self._create_tables()
            
            logger.info("SQLite database initialized successfully")
        except sqlite3.Error as e:
            logger.error(f"SQLite initialization error: {str(e)}")
            raise
    
    def _create_tables(self):
        """Create necessary tables in SQLite database"""
        cursor = self.conn.cursor()
        
        # Create posts table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY,
            title TEXT,
            slug TEXT,
            identifier TEXT,
            comment_count INTEGER,
            upvote_count INTEGER,
            view_count INTEGER,
            exit_count INTEGER,
            rating_count INTEGER,
            average_rating INTEGER,
            share_count INTEGER,
            bookmark_count INTEGER,
            video_link TEXT,
            thumbnail_url TEXT,
            gif_thumbnail_url TEXT,
            contract_address TEXT,
            chain_id TEXT,
            chart_url TEXT,
            created_at INTEGER,
            is_available_in_public_feed BOOLEAN,
            is_locked BOOLEAN,
            tags TEXT,
            raw_data TEXT
        )
        ''')
        
        # Create owners table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS owners (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            post_id INTEGER,
            first_name TEXT,
            last_name TEXT,
            name TEXT,
            username TEXT,
            picture_url TEXT,
            user_type TEXT,
            has_evm_wallet BOOLEAN,
            has_solana_wallet BOOLEAN,
            FOREIGN KEY (post_id) REFERENCES posts (id)
        )
        ''')
        
        # Create categories table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY,
            name TEXT,
            count INTEGER,
            description TEXT,
            image_url TEXT
        )
        ''')
        
        # Create post_category relationship table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS post_category (
            post_id INTEGER,
            category_id INTEGER,
            PRIMARY KEY (post_id, category_id),
            FOREIGN KEY (post_id) REFERENCES posts (id),
            FOREIGN KEY (category_id) REFERENCES categories (id)
        )
        ''')
        
        # Create topics table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS topics (
            id INTEGER PRIMARY KEY,
            name TEXT,
            description TEXT,
            image_url TEXT,
            slug TEXT,
            is_public BOOLEAN,
            project_code TEXT,
            posts_count INTEGER,
            language TEXT,
            created_at TEXT
        )
        ''')
        
        # Create topic_owner table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS topic_owners (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            topic_id INTEGER,
            first_name TEXT,
            last_name TEXT,
            name TEXT,
            username TEXT,
            profile_url TEXT,
            user_type TEXT,
            has_evm_wallet BOOLEAN,
            has_solana_wallet BOOLEAN,
            FOREIGN KEY (topic_id) REFERENCES topics (id)
        )
        ''')
        
        # Create post_topic relationship table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS post_topic (
            post_id INTEGER,
            topic_id INTEGER,
            PRIMARY KEY (post_id, topic_id),
            FOREIGN KEY (post_id) REFERENCES posts (id),
            FOREIGN KEY (topic_id) REFERENCES topics (id)
        )
        ''')
        
        # Create base_tokens table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS base_tokens (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            post_id INTEGER,
            address TEXT,
            name TEXT,
            symbol TEXT,
            image_url TEXT,
            FOREIGN KEY (post_id) REFERENCES posts (id)
        )
        ''')
        
        # Create users table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            first_name TEXT,
            last_name TEXT,
            name TEXT,
            username TEXT,
            profile_url TEXT,
            user_type TEXT,
            has_evm_wallet BOOLEAN,
            has_solana_wallet BOOLEAN,
            raw_data TEXT
        )
        ''')
        
        # Create data_sources table to track which endpoints we've fetched from
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS data_sources (
            name TEXT PRIMARY KEY,
            last_updated INTEGER,
            status TEXT,
            record_count INTEGER
        )
        ''')
        
        self.conn.commit()
    
    def insert_posts(self, posts_data, source_name):
        """Insert posts data into SQLite database"""
        if not isinstance(posts_data, list):
            logger.warning(f"Invalid posts data format for {source_name}")
            return 0
        
        if not posts_data:
            logger.warning(f"Empty posts array in {source_name}")
            return 0
        
        # Clean records to ensure SQLite compatibility
        posts_data = self.clean_records(posts_data)
        
        cursor = self.conn.cursor()
        count = 0
        
        try:
            for post in posts_data:
                # Insert post
                post_id = post.get("id")
                if post_id is None:
                    logger.warning("Skipping post with no ID")
                    continue
                
                # Extract fields, defaulting to None if not present
                cursor.execute('''
                INSERT OR REPLACE INTO posts (
                    id, title, slug, identifier, comment_count, upvote_count, view_count,
                    exit_count, rating_count, average_rating, share_count, bookmark_count,
                    video_link, thumbnail_url, gif_thumbnail_url, contract_address, chain_id,
                    chart_url, created_at, is_available_in_public_feed, is_locked, tags, raw_data
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    post_id,
                    post.get("title"),
                    post.get("slug"),
                    post.get("identifier"),
                    post.get("comment_count"),
                    post.get("upvote_count"),
                    post.get("view_count"),
                    post.get("exit_count"),
                    post.get("rating_count"),
                    post.get("average_rating"),
                    post.get("share_count"),
                    post.get("bookmark_count"),
                    post.get("video_link"),
                    post.get("thumbnail_url"),
                    post.get("gif_thumbnail_url"),
                    post.get("contract_address"),
                    post.get("chain_id"),
                    post.get("chart_url"),
                    post.get("created_at"),
                    post.get("is_available_in_public_feed"),
                    post.get("is_locked"),
                    post.get("tags"),  # Already converted to JSON string in clean_records
                    post.get("raw_data", json.dumps(post))
                ))
                
                # Insert owner
                owner = post.get("owner")
                if owner and isinstance(owner, dict):
                    cursor.execute('''
                    INSERT OR REPLACE INTO owners (
                        post_id, first_name, last_name, name, username, picture_url,
                        user_type, has_evm_wallet, has_solana_wallet
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        post_id,
                        owner.get("first_name"),
                        owner.get("last_name"),
                        owner.get("name"),
                        owner.get("username"),
                        owner.get("picture_url"),
                        owner.get("user_type"),
                        owner.get("has_evm_wallet"),
                        owner.get("has_solana_wallet")
                    ))
                
                # Insert category
                category = post.get("category")
                if category and isinstance(category, dict):
                    cursor.execute('''
                    INSERT OR REPLACE INTO categories (
                        id, name, count, description, image_url
                    ) VALUES (?, ?, ?, ?, ?)
                    ''', (
                        category.get("id"),
                        category.get("name"),
                        category.get("count"),
                        category.get("description"),
                        category.get("image_url")
                    ))
                    
                    # Create post-category relationship
                    cursor.execute('''
                    INSERT OR REPLACE INTO post_category (
                        post_id, category_id
                    ) VALUES (?, ?)
                    ''', (
                        post_id,
                        category.get("id")
                    ))
                
                # Insert topic
                topic = post.get("topic")
                if topic and isinstance(topic, dict):
                    cursor.execute('''
                    INSERT OR REPLACE INTO topics (
                        id, name, description, image_url, slug, is_public,
                        project_code, posts_count, language, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        topic.get("id"),
                        topic.get("name"),
                        topic.get("description"),
                        topic.get("image_url"),
                        topic.get("slug"),
                        topic.get("is_public"),
                        topic.get("project_code"),
                        topic.get("posts_count"),
                        topic.get("language"),
                        topic.get("created_at")
                    ))
                    
                    # Insert topic owner
                    topic_owner = topic.get("owner")
                    if topic_owner and isinstance(topic_owner, dict):
                        cursor.execute('''
                        INSERT OR REPLACE INTO topic_owners (
                            topic_id, first_name, last_name, name, username,
                            profile_url, user_type, has_evm_wallet, has_solana_wallet
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                        ''', (
                            topic.get("id"),
                            topic_owner.get("first_name"),
                            topic_owner.get("last_name"),
                            topic_owner.get("name"),
                            topic_owner.get("username"),
                            topic_owner.get("profile_url"),
                            topic_owner.get("user_type"),
                            topic_owner.get("has_evm_wallet", False),
                            topic_owner.get("has_solana_wallet", False)
                        ))
                    
                    # Create post-topic relationship
                    cursor.execute('''
                    INSERT OR REPLACE INTO post_topic (
                        post_id, topic_id
                    ) VALUES (?, ?)
                    ''', (
                        post_id,
                        topic.get("id")
                    ))
                
                # Insert base token
                base_token = post.get("baseToken")
                if base_token and isinstance(base_token, dict):
                    cursor.execute('''
                    INSERT OR REPLACE INTO base_tokens (
                        post_id, address, name, symbol, image_url
                    ) VALUES (?, ?, ?, ?, ?)
                    ''', (
                        post_id,
                        base_token.get("address"),
                        base_token.get("name"),
                        base_token.get("symbol"),
                        base_token.get("image_url")
                    ))
                
                count += 1
            
            # Update data source
            cursor.execute('''
            INSERT OR REPLACE INTO data_sources (
                name, last_updated, status, record_count
            ) VALUES (?, ?, ?, ?)
            ''', (
                source_name,
                int(time.time()),
                "success",
                count
            ))
            
            self.conn.commit()
            logger.info(f"Successfully inserted {count} posts from {source_name}")
            return count
            
        except sqlite3.Error as e:
            self.conn.rollback()
            logger.error(f"SQLite error inserting posts from {source_name}: {str(e)}")
            raise
    
    def insert_users(self, users_data):
        """Insert users data into SQLite database"""
        if not isinstance(users_data, list):
            logger.warning("Invalid users data format")
            return 0
        
        if not users_data:
            logger.warning("Empty users array")
            return 0
        
        # Clean records to ensure SQLite compatibility
        users_data = self.clean_records(users_data)
        
        cursor = self.conn.cursor()
        count = 0
        
        try:
            for user in users_data:
                user_id = user.get("id")
                if user_id is None:
                    logger.warning("Skipping user with no ID")
                    continue
                
                cursor.execute('''
                INSERT OR REPLACE INTO users (
                    id, first_name, last_name, name, username, profile_url,
                    user_type, has_evm_wallet, has_solana_wallet, raw_data
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    user_id,
                    user.get("first_name"),
                    user.get("last_name"),
                    user.get("name"),
                    user.get("username"),
                    user.get("profile_url"),
                    user.get("user_type"),
                    user.get("has_evm_wallet"),
                    user.get("has_solana_wallet"),
                    json.dumps(user)
                ))
                
                count += 1
            
            # Update data source
            cursor.execute('''
            INSERT OR REPLACE INTO data_sources (
                name, last_updated, status, record_count
            ) VALUES (?, ?, ?, ?)
            ''', (
                "all_users",
                int(time.time()),
                "success",
                count
            ))
            
            self.conn.commit()
            logger.info(f"Successfully inserted {count} users")
            return count
            
        except sqlite3.Error as e:
            self.conn.rollback()
            logger.error(f"SQLite error inserting users: {str(e)}")
            raise
    
    def clean_records(self, records):
        """
        Cleans and flattens records to ensure they are SQLite-compatible.
        Converts unsupported types like dicts/lists to JSON strings.
        """
        cleaned = []
        for record in records:
            cleaned_record = {}
            for k, v in record.items():
                if isinstance(v, (dict, list)):
                    cleaned_record[k] = json.dumps(v)
                else:
                    cleaned_record[k] = v
            cleaned.append(cleaned_record)
        return cleaned
    
    def close(self):
        """Close SQLite connection"""
        if self.conn:
            self.conn.close()
            logger.info("SQLite connection closed")


FLIC_TOKEN = "flic_11d3da28e403d182c36a3530453e290add87d0b4a40ee50f17611f180d47956f"
HEADERS = {"Flic-Token": FLIC_TOKEN}

API_ENDPOINTS = {
    "viewed": "https://api.socialverseapp.com/posts/view?page={page}&page_size=1000&resonance_algorithm=resonance_algorithm_cjsvervb7dbhss8bdrj89s44jfjdbsjd0xnjkbvuire8zcjwerui3njfbvsujc5if",
    "liked": "https://api.socialverseapp.com/posts/like?page={page}&page_size=1000&resonance_algorithm=resonance_algorithm_cjsvervb7dbhss8bdrj89s44jfjdbsjd0xnjkbvuire8zcjwerui3njfbvsujc5if",
    "inspired": "https://api.socialverseapp.com/posts/inspire?page={page}&page_size=1000&resonance_algorithm=resonance_algorithm_cjsvervb7dbhss8bdrj89s44jfjdbsjd0xnjkbvuire8zcjwerui3njfbvsujc5if",
    "rated": "https://api.socialverseapp.com/posts/rating?page={page}&page_size=1000&resonance_algorithm=resonance_algorithm_cjsvervb7dbhss8bdrj89s44jfjdbsjd0xnjkbvuire8zcjwerui3njfbvsujc5if",
    "posts": "https://api.socialverseapp.com/posts/summary/get?page={page}&page_size=1000",
    "users": "https://api.socialverseapp.com/users/get_all?page={page}&page_size=1000"
}

# Database Configuration
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "neo4jpassword")

# Embedding dimension (kept for generating embeddings that will be stored in Neo4j)
EMBEDDING_DIM = 384

class APIDataFetcher:
    """Fetch data from social network API"""
    
    def __init__(self, headers=HEADERS, endpoints=API_ENDPOINTS):
        self.headers = headers
        self.endpoints = endpoints
    
    def fetch_all_paginated(self, endpoint_name, result_key):
        """Fetch all pages of data from a paginated API endpoint"""
        print(f"Fetching {endpoint_name} data...")
        results = []
        page = 1
        
        with tqdm(desc=f"Fetching {endpoint_name}", unit="page") as pbar:
            while True:
                url = self.endpoints[endpoint_name].format(page=page)
                resp = requests.get(url, headers=self.headers)
                resp.raise_for_status()
                data = resp.json()
                items = data.get(result_key, [])
                
                if not items:
                    break
                    
                results.extend(items)
                pbar.update(1)
                
                if len(items) < 1000:  # Less than page size means we've reached the end
                    break
                    
                page += 1
                
        print(f"Fetched {len(results)} {endpoint_name}")
        return results
    
    def fetch_all_data(self):
        """Fetch all data from all endpoints"""
        data = {}
        
        # Fetch all data types
        data["viewed"] = pd.DataFrame(self.fetch_all_paginated("viewed", "posts"))
        data["liked"] = pd.DataFrame(self.fetch_all_paginated("liked", "posts"))
        data["inspired"] = pd.DataFrame(self.fetch_all_paginated("inspired", "posts"))
        data["rated"] = pd.DataFrame(self.fetch_all_paginated("rated", "posts"))
        data["posts"] = pd.DataFrame(self.fetch_all_paginated("posts", "posts"))
        data["users"] = pd.DataFrame(self.fetch_all_paginated("users", "users"))
        
        # Standardize timestamp columns
        data["viewed"] = data["viewed"].rename(columns={"viewed_at": "timestamp"})
        data["liked"] = data["liked"].rename(columns={"liked_at": "timestamp"})
        data["inspired"] = data["inspired"].rename(columns={"inspired_at": "timestamp"})
        data["rated"] = data["rated"].rename(columns={"rated_at": "timestamp"})
        
        # Deduplicate
        for interaction_type in ["viewed", "liked", "inspired", "rated"]:
            data[interaction_type] = data[interaction_type].drop_duplicates(subset=["user_id", "post_id"])
        
        return data
    
    def process_interactions(self, data):
        """Process interaction data and create a unified edge list"""
        # Define interaction weights
        INTERACTION_WEIGHTS = {
            "viewed": 1,
            "liked": 3,
            "inspired": 4,
            "rated": None  # Use actual rating value
        }
        
        def interaction_edges(df, interaction_type, weight=None):
            df = df.copy()
            if interaction_type == "rated":
                df = df[df["rating_percent"].notnull()]
                df["weight"] = df["rating_percent"].astype(float) / 100.0  # Scale 0-100 to 0-1
            else:
                df["weight"] = weight
            df["interaction_type"] = interaction_type
            return df[["user_id", "post_id", "weight", "interaction_type", "timestamp"]]
        
        print("Building edge list...")
        edges = pd.concat([
            interaction_edges(data["viewed"], "viewed", INTERACTION_WEIGHTS["viewed"]),
            interaction_edges(data["liked"], "liked", INTERACTION_WEIGHTS["liked"]),
            interaction_edges(data["inspired"], "inspired", INTERACTION_WEIGHTS["inspired"]),
            interaction_edges(data["rated"], "rated")
        ], ignore_index=True)
        
        # Normalize timestamps and compute recency/strength
        edges["timestamp"] = pd.to_datetime(edges["timestamp"])
        max_time = edges["timestamp"].max()
        min_time = edges["timestamp"].min()
        edges["recency"] = (edges["timestamp"] - min_time) / (max_time - min_time + pd.Timedelta(seconds=1))
        edges["recency"] = edges["recency"].astype(float)
        edges["strength"] = edges["weight"] * (1 + edges["recency"])
        
        return edges
    
    def prepare_data_for_neo4j(self, data, edges):
        users = data["users"].copy()
        users = users.rename(columns={"id": "id"})
        
        # Process posts
        posts = data["posts"].copy()
        posts = posts.rename(columns={"id": "id"})
        
        # Extract category information
        def extract_category_id(category):
            if isinstance(category, dict):
                return category.get("id", 0)
            return 0
            
        def extract_category_name(category):
            if isinstance(category, dict):
                return category.get("name", "Unknown")
            return "Unknown"
            
        # Extract project code from topic
        def extract_project_code(topic):
                if isinstance(topic, list) and topic:
                    return topic[0].get("project_code", "") if isinstance(topic[0], dict) else ""
                return ""

            
        posts["category_id"] = posts["category"].apply(extract_category_id)
        posts["category_name"] = posts["category"].apply(extract_category_name)
        posts["project_code"] = posts["topic"].apply(extract_project_code)
        
        # Process interactions for Neo4j
        # Split interactions into train/val/test sets based on time
        edges_sorted = edges.sort_values("timestamp")
        train_frac, val_frac = 0.8, 0.1
        n = len(edges_sorted)
        train_cutoff_time = edges_sorted.iloc[int(n*train_frac)]["timestamp"]
        val_cutoff_time = edges_sorted.iloc[int(n*(train_frac+val_frac))]["timestamp"]

        train_edges = edges_sorted[edges_sorted["timestamp"] <= train_cutoff_time]
        val_edges = edges_sorted[(edges_sorted["timestamp"] > train_cutoff_time) & 
                               (edges_sorted["timestamp"] <= val_cutoff_time)]
        test_edges = edges_sorted[edges_sorted["timestamp"] > val_cutoff_time]
        
        interactions = {
            "train": train_edges.to_dict('records'),
            "validation": val_edges.to_dict('records'),
            "test": test_edges.to_dict('records')
        }
        
        return {
            "users": users.to_dict('records'),
            "posts": posts.to_dict('records'),
            "interactions": interactions
        }

class Neo4jHandler:
    """Handle Neo4j database operations"""
    
    def __init__(self, uri=NEO4J_URI, user=NEO4J_USER, password=NEO4J_PASSWORD):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
    
    def close(self):
        """Close the Neo4j driver"""
        self.driver.close()
    
    def run_query(self, query, params=None):
        """Run a Neo4j query"""
        with self.driver.session() as session:
            result = session.run(query, params or {})
            return result.data()
    
    def setup_schema(self):
        """Set up Neo4j schema with constraints and indexes"""
        # Create constraints
        self.run_query("CREATE CONSTRAINT IF NOT EXISTS FOR (u:User) REQUIRE u.id IS UNIQUE")
        self.run_query("CREATE CONSTRAINT IF NOT EXISTS FOR (p:Post) REQUIRE p.id IS UNIQUE")
        
        # Create indexes
        self.run_query("CREATE INDEX IF NOT EXISTS FOR (u:User) ON (u.username)")
        self.run_query("CREATE INDEX IF NOT EXISTS FOR (p:Post) ON (p.title)")
        self.run_query("CREATE INDEX IF NOT EXISTS FOR (p:Post) ON (p.category_id)")
        
        print("Neo4j schema setup complete")
    
    def save_users(self, users):
        """Save users to Neo4j"""
        print(f"Saving {len(users)} users to Neo4j...")
        batch_size = 1000
        
        for i in range(0, len(users), batch_size):
            batch = users[i:i+batch_size]
            params = {"users": batch}
            
            query = """
            UNWIND $users AS user
            MERGE (u:User {id: user.id})
            SET 
                u.username = user.username,
                u.first_name = user.first_name,
                u.last_name = user.last_name,
                u.email = user.email,
                u.bio = user.bio,
                u.created_at = user.created_at,
                u.updated_at = user.updated_at
            """
            
            # Add embedding to Neo4j if available
            if "embedding" in batch[0]:
                query += ", u.embedding = user.embedding"
            
            self.run_query(query, params)
            
            if (i + batch_size) % 5000 == 0 or (i + batch_size) >= len(users):
                print(f"Saved {min(i + batch_size, len(users))} users")
                
    def save_posts(self, posts):
        """Save posts to Neo4j"""
        print(f"Saving {len(posts)} posts to Neo4j...")
        batch_size = 1000
        
        for i in range(0, len(posts), batch_size):
            batch = posts[i:i+batch_size]
            params = {"posts": batch}
            
            query = """
            UNWIND $posts AS post
            MERGE (p:Post {id: post.id})
            SET 
                p.title = post.title,
                p.content = post.content,
                p.category_id = post.category_id,
                p.category_name = post.category_name,
                p.project_code = post.project_code,
                p.created_at = post.created_at,
                p.updated_at = post.updated_at
            """
            
            # Add embedding to Neo4j if available
            if "embedding" in batch[0]:
                query += ", p.embedding = post.embedding"
            
            self.run_query(query, params)
            
            if (i + batch_size) % 5000 == 0 or (i + batch_size) >= len(posts):
                print(f"Saved {min(i + batch_size, len(posts))} posts")
            
    def save_interactions(self, interactions):
        """Save user-post interactions to Neo4j"""
        for split, edges in interactions.items():
            print(f"Saving {len(edges)} {split} interactions to Neo4j...")
            batch_size = 1000
            
            for i in range(0, len(edges), batch_size):
                batch = edges[i:i+batch_size]
                params = {"interactions": batch, "split": split}
                
                query = """
                UNWIND $interactions AS interaction
                MATCH (u:User {id: interaction.user_id})
                MATCH (p:Post {id: interaction.post_id})
                MERGE (u)-[r:INTERACTED {split: $split}]->(p)
                SET 
                    r.type = interaction.interaction_type,
                    r.weight = interaction.weight,
                    r.timestamp = datetime(interaction.timestamp),
                    r.recency = interaction.recency,
                    r.strength = interaction.strength
                """
                
                self.run_query(query, params)
                
                if (i + batch_size) % 5000 == 0 or (i + batch_size) >= len(edges):
                    print(f"Saved {min(i + batch_size, len(edges))} {split} interactions")

class SocialNetworkDataProcessor:
    """Process social network data and generate embeddings"""
    
    def __init__(self):
        # Initialize embedding model
        try:
            from sentence_transformers import SentenceTransformer
            self.model = SentenceTransformer('all-MiniLM-L6-v2')
            self.embedding_available = True
        except ImportError:
            print("Warning: sentence-transformers not available. Using random embeddings.")
            self.embedding_available = False
    
    def generate_embeddings(self, data):
        """Generate embeddings for users and posts"""
        print("Generating embeddings...")
        
        # Generate user embeddings
        users = data["users"]
        for user in tqdm(users, desc="Generating user embeddings"):
            user_text = f"{user.get('username', '')} {user.get('first_name', '')} {user.get('last_name', '')} {user.get('bio', '')}"
            if self.embedding_available:
                user["embedding"] = self.model.encode(user_text).tolist()
            else:
                user["embedding"] = np.random.rand(EMBEDDING_DIM).astype(np.float32).tolist()
        
        # Generate post embeddings
        posts = data["posts"]
        for post in tqdm(posts, desc="Generating post embeddings"):
            post_text = f"{post.get('title', '')} {post.get('content', '')}"
            if self.embedding_available:
                post["embedding"] = self.model.encode(post_text).tolist()
            else:
                post["embedding"] = np.random.rand(EMBEDDING_DIM).astype(np.float32).tolist()
        
        return data

class DataAnalyzer:
    """Class for analyzing data and cleaning low-quality records from databases"""
    
    def __init__(self, sqlite_handler, neo4j_handler=None):
        self.sqlite = sqlite_handler
        self.neo4j = neo4j_handler
        self.none_threshold = 0.6  # If more than 60% of fields are None, consider it low quality
    
    def generate_sqlite_summary(self):
        """Generate a summary of data in SQLite database"""
        conn = self.sqlite.conn
        cursor = conn.cursor()
        
        # Get table counts
        tables = [
            "posts", "owners", "categories", "topics", 
            "topic_owners", "base_tokens", "users"
        ]
        summary = {}
        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            summary[table] = count
        
        # Get data sources summary
        cursor.execute("SELECT name, last_updated, status, record_count FROM data_sources")
        sources = cursor.fetchall()
        summary["data_sources"] = []
        
        for source in sources:
            summary["data_sources"].append({
                "name": source[0],
                "last_updated": datetime.fromtimestamp(source[1]).strftime('%Y-%m-%d %H:%M:%S'),
                "status": source[2],
                "record_count": source[3]
            })
        
        return summary
    
    def analyze_data_quality(self):
        """Analyze data quality in both databases and identify low-quality records"""
        quality_report = {
            "sqlite": self._analyze_sqlite_quality(),
            "neo4j": self._analyze_neo4j_quality() if self.neo4j else {"status": "skipped", "reason": "Neo4j handler not provided"}
        }
        
        return quality_report
    
    def _analyze_sqlite_quality(self):
        """Analyze data quality in SQLite database"""
        conn = self.sqlite.conn
        cursor = conn.cursor()
        quality_report = {}
        
        # Analyze main tables
        tables = ["posts", "owners", "users", "topics"]
        
        for table in tables:
            # Get column names
            cursor.execute(f"PRAGMA table_info({table})")
            columns = [row[1] for row in cursor.fetchall() if row[1] != 'raw_data']
            
            if not columns:
                quality_report[table] = {"status": "error", "message": "No columns found"}
                continue
            
            # Count total rows
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            total_rows = cursor.fetchone()[0]
            
            # Count NULL values for each column
            null_counts = {}
            for column in columns:
                cursor.execute(f"SELECT COUNT(*) FROM {table} WHERE {column} IS NULL")
                null_count = cursor.fetchone()[0]
                null_counts[column] = null_count
            
            # Identify low-quality rows (rows with majority NULL values)
            null_conditions = [f"{col} IS NULL" for col in columns]
            query = f"""
            SELECT id, COUNT(*) as null_count
            FROM {table}
            WHERE {' OR '.join(null_conditions)}
            GROUP BY id
            HAVING null_count > {int(len(columns) * self.none_threshold)}
            """
            
            try:
                cursor.execute(query)
                low_quality_ids = [row[0] for row in cursor.fetchall()]
            except sqlite3.Error:
                # Fallback if the query fails (e.g., if 'id' column doesn't exist)
                low_quality_ids = []
            
            quality_report[table] = {
                "total_rows": total_rows,
                "null_counts": null_counts,
                "low_quality_count": len(low_quality_ids),
                "low_quality_ids": low_quality_ids[:100]  # Limit to first 100 IDs
            }
        
        return quality_report
    
    def _analyze_neo4j_quality(self):
        """Analyze data quality in Neo4j database"""
        if not self.neo4j:
            return {"status": "error", "message": "Neo4j handler not provided"}
        
        quality_report = {}
        
        # Analyze User nodes
        user_query = """
        MATCH (u:User)
        WITH u, 
            size([p in keys(u) WHERE p <> 'id' AND u[p] IS NULL]) AS null_count,
            size(keys(u)) - 1 AS total_props
        RETURN 
            count(u) AS total_users,
            sum(CASE WHEN 1.0 * null_count / total_props > $threshold THEN 1 ELSE 0 END) AS low_quality_count,
            collect(CASE WHEN 1.0 * null_count / total_props > $threshold THEN u.id ELSE NULL END) AS low_quality_ids
        """
        
        user_result = self.neo4j.run_query(user_query, {"threshold": self.none_threshold})
        if user_result:
            quality_report["users"] = {
                "total_rows": user_result[0]["total_users"],
                "low_quality_count": user_result[0]["low_quality_count"],
                "low_quality_ids": [id for id in user_result[0]["low_quality_ids"] if id is not None][:100]
            }
        
        # Analyze Post nodes
        post_query = """
        MATCH (p:Post)
        WITH p, 
            size([prop in keys(p) WHERE prop <> 'id' AND p[prop] IS NULL]) AS null_count,
            size(keys(p)) - 1 AS total_props
        RETURN 
            count(p) AS total_posts,
            sum(CASE WHEN 1.0 * null_count / total_props > $threshold THEN 1 ELSE 0 END) AS low_quality_count,
            collect(CASE WHEN 1.0 * null_count / total_props > $threshold THEN p.id ELSE NULL END) AS low_quality_ids
        """
        
        post_result = self.neo4j.run_query(post_query, {"threshold": self.none_threshold})
        if post_result:
            quality_report["posts"] = {
                "total_rows": post_result[0]["total_posts"],
                "low_quality_count": post_result[0]["low_quality_count"],
                "low_quality_ids": [id for id in post_result[0]["low_quality_ids"] if id is not None][:100]
            }
        
        return quality_report
    
    def clean_low_quality_data(self, dry_run=False):
        """Remove low-quality data from both databases"""
        # Analyze data quality first
        quality_report = self.analyze_data_quality()
        
        cleaning_report = {
            "sqlite": self._clean_sqlite_data(quality_report["sqlite"], dry_run),
            "neo4j": self._clean_neo4j_data(quality_report["neo4j"], dry_run) if self.neo4j else {"status": "skipped"}
        }
        
        return cleaning_report
    
    def _clean_sqlite_data(self, quality_report, dry_run=False):
        """Remove low-quality data from SQLite database"""
        if not quality_report:
            return {"status": "error", "message": "No quality report provided"}
        
        conn = self.sqlite.conn
        cursor = conn.cursor()
        cleaning_results = {}
        
        for table, report in quality_report.items():
            if "low_quality_ids" not in report or not report["low_quality_ids"]:
                cleaning_results[table] = {"status": "skipped", "reason": "No low-quality records found"}
                continue
            
            # Delete low-quality records
            ids_to_delete = report["low_quality_ids"]
            if not dry_run:
                try:
                    placeholders = ','.join(['?'] * len(ids_to_delete))
                    cursor.execute(f"DELETE FROM {table} WHERE id IN ({placeholders})", ids_to_delete)
                    conn.commit()
                    cleaning_results[table] = {
                        "status": "success", 
                        "deleted_count": cursor.rowcount,
                        "deleted_ids": ids_to_delete
                    }
                except sqlite3.Error as e:
                    conn.rollback()
                    cleaning_results[table] = {"status": "error", "message": str(e)}
            else:
                cleaning_results[table] = {
                    "status": "dry_run", 
                    "would_delete_count": len(ids_to_delete),
                    "would_delete_ids": ids_to_delete
                }
        
        return cleaning_results
    
    def _clean_neo4j_data(self, quality_report, dry_run=False):
        """Remove low-quality data from Neo4j database"""
        if not self.neo4j or not quality_report:
            return {"status": "error", "message": "Neo4j handler not provided or no quality report"}
        
        cleaning_results = {}
        
        # Clean User nodes
        if "users" in quality_report and quality_report["users"]["low_quality_ids"]:
            user_ids = quality_report["users"]["low_quality_ids"]
            
            if not dry_run:
                delete_query = """
                MATCH (u:User)
                WHERE u.id IN $ids
                DETACH DELETE u
                RETURN count(u) as deleted_count
                """
                
                result = self.neo4j.run_query(delete_query, {"ids": user_ids})
                cleaning_results["users"] = {
                    "status": "success",
                    "deleted_count": result[0]["deleted_count"] if result else 0,
                    "deleted_ids": user_ids
                }
            else:
                cleaning_results["users"] = {
                    "status": "dry_run",
                    "would_delete_count": len(user_ids),
                    "would_delete_ids": user_ids
                }
        
        # Clean Post nodes
        if "posts" in quality_report and quality_report["posts"]["low_quality_ids"]:
            post_ids = quality_report["posts"]["low_quality_ids"]
            
            if not dry_run:
                delete_query = """
                MATCH (p:Post)
                WHERE p.id IN $ids
                DETACH DELETE p
                RETURN count(p) as deleted_count
                """
                
                result = self.neo4j.run_query(delete_query, {"ids": post_ids})
                cleaning_results["posts"] = {
                    "status": "success",
                    "deleted_count": result[0]["deleted_count"] if result else 0,
                    "deleted_ids": post_ids
                }
            else:
                cleaning_results["posts"] = {
                    "status": "dry_run",
                    "would_delete_count": len(post_ids),
                    "would_delete_ids": post_ids
                }
        
        return cleaning_results
    
    def export_to_csv(self, output_dir="./export"):
        """Export SQLite data to CSV files"""
        conn = self.sqlite.conn
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Define tables to export
        tables = [
            "posts", "owners", "categories", "topics", 
            "topic_owners", "base_tokens", "users", "data_sources"
        ]
        
        for table in tables:
            try:
                # Read table data
                df = pd.read_sql_query(f"SELECT * FROM {table}", conn)
                
                # Export to CSV
                output_file = os.path.join(output_dir, f"{table}.csv")
                df.to_csv(output_file, index=False)
                logger.info(f"Exported {table} to {output_file}")
            except Exception as e:
                logger.error(f"Error exporting {table} to CSV: {str(e)}")
        
        return output_dir


def run_alembic_migration():
    """Run Alembic database migration"""
    try:
        logger.info("Running Alembic database migration: alembic upgrade head")
        result = subprocess.run(
            ["alembic", "upgrade", "head"], 
            capture_output=True, 
            text=True, 
            check=True
        )
        logger.info(f"Alembic migration completed successfully: {result.stdout}")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Alembic migration failed: {e.stderr}")
        return False
    except Exception as e:
        logger.error(f"Error running Alembic migration: {str(e)}")
        return False
    
def main():
    """Main function to orchestrate the data pipeline"""
    try:
        logger.info("Starting data pipeline")
        
        # Check if we need to run Alembic migration
        if len(sys.argv) > 1 and sys.argv[1] == "alembic" and len(sys.argv) > 2 and sys.argv[2] == "upgrade" and len(sys.argv) > 3 and sys.argv[3] == "head":
            logger.info("Running Alembic migration command")
            success = run_alembic_migration()
            if success:
                logger.info("Alembic migration completed successfully")
                return
            else:
                logger.error("Alembic migration failed")
                sys.exit(1)
        
        # Initialize components
        config = Config()
        api_handler = APIHandler(config)
        sqlite_handler = SQLiteHandler(config)
        
        # Fetch data from all endpoints
        data = api_handler.fetch_all_data()
        
        # Process and store posts data
        for source_name in ["viewed_posts", "liked_posts", "inspired_posts", "rated_posts", "all_posts"]:
            posts_data = data.get(source_name)
            if isinstance(posts_data, list) and posts_data:
                # Insert into SQLite
                sqlite_handler.insert_posts(posts_data, source_name)
        
        # Process and store users data
        users_data = data.get("all_users")
        if isinstance(users_data, list) and users_data:
            # Insert into SQLite
            sqlite_handler.insert_users(users_data)
        
        # Initialize Neo4j components
        data_processor = SocialNetworkDataProcessor()
        neo4j_handler = Neo4jHandler()
        api_fetcher = APIDataFetcher()
        
        try:
            # Set up database schemas
            logger.info("Setting up Neo4j database schema...")
            neo4j_handler.setup_schema()
            
            # Fetch data from API
            logger.info("Fetching data from API...")
            raw_data = api_fetcher.fetch_all_data()
            
            # Process interactions
            edges = api_fetcher.process_interactions(raw_data)
            
            # Prepare data for Neo4j
            logger.info("Preparing data for Neo4j...")
            neo4j_data = api_fetcher.prepare_data_for_neo4j(raw_data, edges)
            
            # Generate embeddings
            logger.info("Generating embeddings...")
            neo4j_data = data_processor.generate_embeddings(neo4j_data)
            
            # Save data to Neo4j
            logger.info("Saving data to Neo4j...")
            neo4j_handler.save_users(neo4j_data["users"])
            neo4j_handler.save_posts(neo4j_data["posts"])
            neo4j_handler.save_interactions(neo4j_data["interactions"])
            
            # Create analyzer with both database handlers
            analyzer = DataAnalyzer(sqlite_handler, neo4j_handler)
            
            # Analyze data quality
            logger.info("Analyzing data quality...")
            quality_report = analyzer.analyze_data_quality()
            logger.info(f"Data quality report: {json.dumps(quality_report, indent=2)}")
            
            # Clean low-quality data
            # First do a dry run to see what would be deleted
            logger.info("Performing dry run of data cleaning...")
            dry_run_report = analyzer.clean_low_quality_data(dry_run=True)
            logger.info(f"Dry run cleaning report: {json.dumps(dry_run_report, indent=2)}")
            
            # Ask for confirmation before actual deletion
            if len(sys.argv) > 1 and sys.argv[1] == "--force-clean":
                do_clean = True
            else:
                user_input = input("Do you want to proceed with removing low-quality data? (y/n): ")
                do_clean = user_input.lower() in ['y', 'yes']
            
            if do_clean:
                logger.info("Cleaning low-quality data...")
                cleaning_report = analyzer.clean_low_quality_data(dry_run=False)
                logger.info(f"Cleaning report: {json.dumps(cleaning_report, indent=2)}")
            else:
                logger.info("Data cleaning skipped by user")
            
            # Generate SQLite summary after cleaning
            sqlite_summary = analyzer.generate_sqlite_summary()
            
            # Export data to CSV
            export_dir = analyzer.export_to_csv()
            
            logger.info("Data loading and cleaning completed successfully!")
            logger.info(f"SQLite Summary: {json.dumps(sqlite_summary, indent=2)}")
            logger.info(f"Data exported to CSV files in {export_dir}")
            
        except Exception as e:
            logger.error(f"Error during Neo4j data loading or analysis: {str(e)}")
            import traceback
            traceback.print_exc()
        
        finally:
            # Clean up Neo4j connection
            neo4j_handler.close()
            # Close SQLite connection
            sqlite_handler.close()
        
    except Exception as e:
        logger.error(f"Pipeline failed: {str(e)}")
        # Ensure database connections are closed on error
        try:
            sqlite_handler.close()
        except Exception:
            pass
        
        try:
            neo4j_handler.close()
        except Exception:
            pass
            
        sys.exit(1)


if __name__ == "__main__":
    main()