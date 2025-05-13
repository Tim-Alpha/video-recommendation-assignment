import requests
import pandas as pd
import torch
from datetime import datetime
import logging
from app.core.config import settings
from app.models.database import neo4j_db

logger = logging.getLogger(__name__)

class DataService:
    def __init__(self):
        self.headers = {"Flic-Token": settings.FLIC_TOKEN}
        self.api_endpoints = {
            "viewed": f"{settings.API_BASE_URL}/posts/view?page={{page}}&page_size=1000&resonance_algorithm=resonance_algorithm_cjsvervb7dbhss8bdrj89s44jfjdbsjd0xnjkbvuire8zcjwerui3njfbvsujc5if",
            "liked": f"{settings.API_BASE_URL}/posts/like?page={{page}}&page_size=1000&resonance_algorithm=resonance_algorithm_cjsvervb7dbhss8bdrj89s44jfjdbsjd0xnjkbvuire8zcjwerui3njfbvsujc5if",
            "inspired": f"{settings.API_BASE_URL}/posts/inspire?page={{page}}&page_size=1000&resonance_algorithm=resonance_algorithm_cjsvervb7dbhss8bdrj89s44jfjdbsjd0xnjkbvuire8zcjwerui3njfbvsujc5if",
            "rated": f"{settings.API_BASE_URL}/posts/rating?page={{page}}&page_size=1000&resonance_algorithm=resonance_algorithm_cjsvervb7dbhss8bdrj89s44jfjdbsjd0xnjkbvuire8zcjwerui3njfbvsujc5if",
            "posts": f"{settings.API_BASE_URL}/posts/summary/get?page={{page}}&page_size=1000",
            "users": f"{settings.API_BASE_URL}/users/get_all?page={{page}}&page_size=1000"
        }
        self.db = neo4j_db
    
    async def fetch_all_data(self):
        """Fetch all data from API endpoints and store in Neo4j"""
        try:
            logger.info("Starting data fetch from API endpoints")
            
            # Fetch data from all endpoints
            data = {}
            data["viewed"] = pd.DataFrame(await self._fetch_all_paginated("viewed", "posts"))
            data["liked"] = pd.DataFrame(await self._fetch_all_paginated("liked", "posts"))
            data["inspired"] = pd.DataFrame(await self._fetch_all_paginated("inspired", "posts"))
            data["rated"] = pd.DataFrame(await self._fetch_all_paginated("rated", "posts"))
            data["posts"] = pd.DataFrame(await self._fetch_all_paginated("posts", "posts"))
            data["users"] = pd.DataFrame(await self._fetch_all_paginated("users", "users"))
            
            # Standardize timestamp columns
            data["viewed"] = data["viewed"].rename(columns={"viewed_at": "timestamp"})
            data["liked"] = data["liked"].rename(columns={"liked_at": "timestamp"})
            data["inspired"] = data["inspired"].rename(columns={"inspired_at": "timestamp"})
            data["rated"] = data["rated"].rename(columns={"rated_at": "timestamp"})
            
            # Deduplicate
            for interaction_type in ["viewed", "liked", "inspired", "rated"]:
                data[interaction_type] = data[interaction_type].drop_duplicates(subset=["user_id", "post_id"])
            
            # Process interactions
            edges = await self._process_interactions(data)
            
            # Prepare data for Neo4j
            neo4j_data = await self._prepare_data_for_neo4j(data, edges)
            
            # Save to Neo4j
            await self._save_to_neo4j(neo4j_data)
            
            logger.info("Data fetch and storage completed successfully")
            return {"status": "success", "message": "Data fetch and storage completed successfully"}
        except Exception as e:
            logger.error(f"Error fetching data: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    async def _fetch_all_paginated(self, endpoint_name, result_key):
        """Fetch all pages from a paginated API endpoint"""
        results = []
        page = 1
        
        while True:
            url = self.api_endpoints[endpoint_name].format(page=page)
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            
            data = response.json()
            items = data.get(result_key, [])
            
            if not items:
                break
                
            results.extend(items)
            
            if len(items) < 1000:  # Less than page size means we've reached the end
                break
                
            page += 1
        
        logger.info(f"Fetched {len(results)} items from {endpoint_name}")
        return results
    
    async def _process_interactions(self, data):
        """Process interaction data and create edge list"""
        # Define interaction weights
        interaction_weights = {
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
        
        edges = pd.concat([
            interaction_edges(data["viewed"], "viewed", interaction_weights["viewed"]),
            interaction_edges(data["liked"], "liked", interaction_weights["liked"]),
            interaction_edges(data["inspired"], "inspired", interaction_weights["inspired"]),
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
    
    async def _prepare_data_for_neo4j(self, data, edges):
        """Prepare data for Neo4j database"""
        # Process users
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
        
        posts["category_id"] = posts["category"].apply(extract_category_id)
        posts["category_name"] = posts["category"].apply(extract_category_name)
        
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
    
    async def _save_to_neo4j(self, data):
        """Save data to Neo4j database"""
        # Set up schema
        self.db.run_query("CREATE CONSTRAINT IF NOT EXISTS FOR (u:User) REQUIRE u.id IS UNIQUE")
        self.db.run_query("CREATE CONSTRAINT IF NOT EXISTS FOR (p:Post) REQUIRE p.id IS UNIQUE")
        self.db.run_query("CREATE INDEX IF NOT EXISTS FOR (u:User) ON (u.username)")
        self.db.run_query("CREATE INDEX IF NOT EXISTS FOR (p:Post) ON (p.title)")
        self.db.run_query("CREATE INDEX IF NOT EXISTS FOR (p:Post) ON (p.category_id)")
        
        # Save users
        logger.info(f"Saving {len(data['users'])} users to Neo4j")
        batch_size = 1000
        for i in range(0, len(data['users']), batch_size):
            batch = data['users'][i:i+batch_size]
            query = """
            UNWIND $users AS user
            MERGE (u:User {id: user.id})
            SET
                u.username = user.username,
                u.first_name = user.first_name,
                u.last_name = user.last_name,
                u.name = user.name,
                u.profile_url = user.profile_url,
                u.user_type = user.user_type,
                u.has_evm_wallet = user.has_evm_wallet,
                u.has_solana_wallet = user.has_solana_wallet
            """
            self.db.run_query(query, {"users": batch})
        
        # Save posts
        logger.info(f"Saving {len(data['posts'])} posts to Neo4j")
        for i in range(0, len(data['posts']), batch_size):
            batch = data['posts'][i:i+batch_size]
            query = """
            UNWIND $posts AS post
            MERGE (p:Post {id: post.id})
            SET
                p.title = post.title,
                p.slug = post.slug,
                p.category_id = post.category_id,
                p.category_name = post.category_name,
                p.view_count = post.view_count,
                p.upvote_count = post.upvote_count,
                p.average_rating = post.average_rating,
                p.thumbnail_url = post.thumbnail_url,
                p.video_link = post.video_link
            """
            self.db.run_query(query, {"posts": batch})
        
        # Save interactions
        for split, edges in data['interactions'].items():
            logger.info(f"Saving {len(edges)} {split} interactions to Neo4j")
            for i in range(0, len(edges), batch_size):
                batch = edges[i:i+batch_size]
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
                self.db.run_query(query, {"interactions": batch, "split": split})

data_service = DataService()
