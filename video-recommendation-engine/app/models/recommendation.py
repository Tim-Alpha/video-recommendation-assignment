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
import torch
from torch_geometric.data import Data
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch_geometric.nn import HeteroConv, GATConv, SAGEConv
from torch_geometric.data import HeteroData
import logging
import os
import requests
import time  
from app.core.config import settings



class MoodEmbedding(nn.Module):
    def __init__(self, num_moods: int, embed_dim: int):
        super().__init__()
        self.embedding = nn.Embedding(num_moods + 1, embed_dim)
        nn.init.xavier_uniform_(self.embedding.weight)
    
    def forward(self, mood_ids):
        mood_ids = torch.clamp(mood_ids, 0, self.embedding.num_embeddings - 1)
        return self.embedding(mood_ids)

class ContentEmbedding(nn.Module):
    def __init__(self, num_categories: int, embed_dim: int):
        super().__init__()
        self.num_categories = num_categories
        self.category_embedding = nn.Embedding(num_categories + 1, embed_dim, padding_idx=0)
        nn.init.xavier_uniform_(self.category_embedding.weight)
        self.batch_norm = nn.BatchNorm1d(3)
    
    def forward(self, x):
        category_ids = x[:, 0].long()
        category_ids = torch.clamp(category_ids, 0, self.num_categories)
        category_embed = self.category_embedding(category_ids)
        
        other_features = x[:, 1:]
        if other_features.shape[0] > 1:
            other_features = self.batch_norm(other_features)
        
        return torch.cat([category_embed, other_features], dim=1)

class HeteroGNNRecommender(nn.Module):
    def __init__(
        self,
        user_feature_dim: int,
        post_feature_dim: int,
        hidden_dim: int = 256,
        num_layers: int = 2,
        dropout: float = 0.0,
        num_moods: int = 4,
        num_categories: int = 14
    ):
        super().__init__()
        self.hidden_dim = hidden_dim
        self.dropout = dropout
        self.num_categories = num_categories
        
        # Feature embeddings with batch normalization
        self.user_embedding = nn.Sequential(
            nn.Linear(user_feature_dim, hidden_dim),
            nn.BatchNorm1d(hidden_dim),
            nn.ReLU(),
            nn.Dropout(dropout)
        )
        
        self.post_embedding = nn.Sequential(
            ContentEmbedding(self.num_categories, hidden_dim // 2),
            nn.Linear(post_feature_dim + (hidden_dim // 2) - 1, hidden_dim),
            nn.BatchNorm1d(hidden_dim),
            nn.ReLU(),
            nn.Dropout(dropout)
        )
        
        # Mood embedding for cold start
        self.mood_embedding = MoodEmbedding(num_moods, hidden_dim)
        
        # Graph Convolution Layers
        self.convs = nn.ModuleList()
        for _ in range(num_layers):
            conv = HeteroConv({
                ('user', 'interacts', 'post'): GATConv((-1, -1), hidden_dim // 2, heads=2, dropout=dropout, add_self_loops=False, concat=True),
                ('post', 'rev_interacts', 'user'): GATConv((-1, -1), hidden_dim // 2, heads=2, dropout=dropout, add_self_loops=False, concat=True),
                ('user', 'similar_to', 'user'): SAGEConv((-1, -1), hidden_dim),
                ('post', 'similar_to', 'post'): SAGEConv((-1, -1), hidden_dim),
            }, aggr='mean')
            self.convs.append(conv)
        
        # Projection layers
        self.user_proj = nn.Linear(hidden_dim, hidden_dim)
        self.post_proj = nn.Linear(hidden_dim, hidden_dim)
        
        # Output prediction layers
        self.post_predictor = nn.Sequential(
            nn.Linear(hidden_dim, hidden_dim),
            nn.BatchNorm1d(hidden_dim),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_dim, 1)
        )
        
        # Cold start prediction layers
        self.cold_start_predictor = nn.Sequential(
            nn.Linear(hidden_dim * 2, hidden_dim),
            nn.BatchNorm1d(hidden_dim),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_dim, 1)
        )
        
        # Initialize weights
        self._init_weights()
    
    def _init_weights(self):
        for module in self.modules():
            if isinstance(module, nn.Linear):
                nn.init.kaiming_normal_(module.weight, mode='fan_out', nonlinearity='relu')
                if module.bias is not None:
                    nn.init.constant_(module.bias, 0)
    
    def forward(self, data: HeteroData):
        x_dict = {
            'user': self.user_embedding(data['user'].x),
            'post': self.post_embedding(data['post'].x)
        }
        
        for conv in self.convs:
            edge_types = [
                ('user', 'interacts', 'post'),
                ('post', 'rev_interacts', 'user'),
                ('user', 'similar_to', 'user'),
                ('post', 'similar_to', 'post')
            ]
            
            edge_index_dict = data.edge_index_dict.copy()
            edge_index_dict = {
                edge_type: edge_index_dict[edge_type] for edge_type in edge_types if edge_type in edge_index_dict
            }
            
            x_dict = conv(x_dict, edge_index_dict)
            x_dict = {key: F.relu(x) for key, x in x_dict.items()}
            x_dict = {key: F.dropout(x, p=self.dropout, training=self.training) for key, x in x_dict.items()}
        
        return x_dict
    
    def recommend(self, data: HeteroData, user_idx: int, top_k: int = 10, exclude_seen: bool = True):
        self.eval()
        with torch.no_grad():
            x_dict = self(data)
            user_emb = x_dict['user'][user_idx].unsqueeze(0)
            post_embs = x_dict['post']
            
            scores = []
            for i, post_emb in enumerate(post_embs):
                score = torch.sigmoid(self.predict_interaction(user_emb, post_emb.unsqueeze(0)))
                scores.append((i, score.item()))
            
            if exclude_seen and ('user', 'interacts', 'post') in data.edge_index_dict:
                seen_mask = (data.edge_index_dict[('user', 'interacts', 'post')][0] == user_idx)
                seen_posts = data.edge_index_dict[('user', 'interacts', 'post')][1][seen_mask].tolist()
                scores = [(i, s) for i, s in scores if i not in seen_posts]
            
            scores.sort(key=lambda x: x[1], reverse=True)
            return scores[:top_k]
    
    def cold_start_recommend(self, data: HeteroData, mood_id: int, top_k: int = 10):
        self.eval()
        with torch.no_grad():
            x_dict = self(data)
            mood_id_tensor = torch.tensor([mood_id], device=data['post'].x.device)
            mood_emb = self.mood_embedding(mood_id_tensor)
            post_embs = x_dict['post']
            
            # Normalize embeddings
            mood_emb = F.normalize(mood_emb, p=2, dim=-1)
            post_embs = F.normalize(post_embs, p=2, dim=-1)
            
            scores = []
            for i, post_emb in enumerate(post_embs):
                combined = torch.cat([mood_emb, post_emb.unsqueeze(0)], dim=1)
                score = torch.sigmoid(self.cold_start_predictor(combined))
                scores.append((i, score.item()))
            
            scores.sort(key=lambda x: x[1], reverse=True)
            return scores[:top_k]
    
    def predict_interaction(self, user_emb: torch.Tensor, post_emb: torch.Tensor):
        user_proj = self.user_proj(user_emb)
        post_proj = self.post_proj(post_emb)
        interaction = user_proj * post_proj
        return self.post_predictor(interaction)


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("data_pipeline.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class RecommendationSystem:
    def __init__(self):
        self.model = None
        self.data = None
        self.user_id_map = {}
        self.post_id_map = {}
        self.reverse_user_map = {}
        self.reverse_post_map = {}
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.recommendation_cache = {}
        self.cache_ttl = settings.CACHE_TTL
        
        self._load_model_and_data()
    
    def _load_model_and_data(self):
        try:
            # Load graph data
            logger.info(f"Loading graph data from {settings.DATA_PATH}")
            self.data = torch.load(settings.DATA_PATH)
            self.data = self.data.to(self.device)
            
            # Extract mappings
            if hasattr(self.data["user"], "node_id"):
                user_ids = self.data["user"].node_id.tolist()
                self.user_id_map = {str(uid): idx for idx, uid in enumerate(user_ids)}
                self.reverse_user_map = {idx: str(uid) for idx, uid in enumerate(user_ids)}
            
            if hasattr(self.data["post"], "node_id"):
                post_ids = self.data["post"].node_id.tolist()
                self.post_id_map = {str(pid): idx for idx, pid in enumerate(post_ids)}
                self.reverse_post_map = {idx: str(pid) for idx, pid in enumerate(post_ids)}
            
            # Load model
            logger.info(f"Loading model from {settings.MODEL_PATH}")
            user_feature_dim = self.data["user"].x.shape[1]
            post_feature_dim = self.data["post"].x.shape[1]
            
            # Create model with appropriate dimensions
            self.model = HeteroGNNRecommender(
                user_feature_dim=user_feature_dim,
                post_feature_dim=post_feature_dim,
                hidden_dim=256,
                num_layers=4,
                dropout=0.2,
                num_moods=4,
                num_categories=13
            )
            
            # Load state dict if model file exists
            if os.path.exists(settings.MODEL_PATH):
                self.model.load_state_dict(torch.load(settings.MODEL_PATH, map_location=self.device))
            
            self.model = self.model.to(self.device)
            self.model.eval()
            
            logger.info("Model and data loaded successfully")
        except Exception as e:
            logger.error(f"Error loading model or data: {str(e)}")
            raise
    
    def get_recommendations(self, username, page=1, page_size=10, category_id=None, mood_id=None):
        # Check if user exists
        user_id = self._get_user_id_by_username(username)
        is_cold_start = user_id is None
        
        # Handle cold start with mood-based recommendations
        if is_cold_start:
            if mood_id is None:
                raise ValueError("Mood ID required for new users")
            return self._get_cold_start_recommendations(mood_id, page, page_size, category_id)
        
        # Convert username to internal user index
        user_idx = self.user_id_map.get(user_id)
        if user_idx is None:
            raise ValueError(f"User {username} not found in model data")
        
        # Create cache key
        cache_key = f"{user_id}_{page}_{page_size}_{category_id}"
        
        # Check cache
        if cache_key in self.recommendation_cache:
            cached_data = self.recommendation_cache[cache_key]
            if (time.time() - cached_data["timestamp"]) < self.cache_ttl:
                logger.info(f"Using cached recommendations for user {username}")
                return cached_data["recommendations"]
        
        # Generate recommendations
        try:
            with torch.no_grad():
                # Get top recommendations
                all_recs = self.model.recommend(
                    self.data,
                    user_idx,
                    top_k=page_size * page * 2,  # Get more than needed for pagination
                    exclude_seen=True
                )
                
                # Filter by category if needed
                if category_id is not None:
                    all_recs = self._filter_by_category(all_recs, category_id)
                
                # Apply pagination
                start_idx = (page - 1) * page_size
                end_idx = min(start_idx + page_size, len(all_recs))
                paged_recs = all_recs[start_idx:end_idx]
                
                # Convert internal indices to external IDs
                recommendations = []
                for post_idx, score in paged_recs:
                    post_id = self.reverse_post_map[post_idx]
                    post_details = self._get_post_details(post_id)
                    recommendations.append({
                        "post_id": post_id,
                        "score": score,
                        "rank": len(recommendations) + 1 + start_idx,
                        "details": post_details
                    })
                
                # Create response
                response = {
                    "username": username,
                    "user_id": user_id,
                    "page": page,
                    "page_size": page_size,
                    "total_items": len(all_recs),
                    "recommendations": recommendations
                }
                
                # Cache the results
                self.recommendation_cache[cache_key] = {
                    "timestamp": time.time(),
                    "recommendations": response
                }
                
                return response
        except Exception as e:
            logger.error(f"Error generating recommendations: {str(e)}")
            raise
    
    def _get_cold_start_recommendations(self, mood_id, page=1, page_size=10, category_id=None):
        # Create cache key
        cache_key = f"mood_{mood_id}_{page}_{page_size}_{category_id}"
        
        # Check cache
        if cache_key in self.recommendation_cache:
            cached_data = self.recommendation_cache[cache_key]
            if (time.time() - cached_data["timestamp"]) < self.cache_ttl:
                logger.info(f"Using cached mood recommendations for mood {mood_id}")
                return cached_data["recommendations"]
        
        # Generate recommendations
        try:
            with torch.no_grad():
                # Get top recommendations based on mood
                all_recs = self.model.cold_start_recommend(
                    self.data,
                    mood_id,
                    top_k=page_size * page * 2  # Get more than needed for pagination
                )
                
                # Filter by category if needed
                if category_id is not None:
                    all_recs = self._filter_by_category(all_recs, category_id)
                
                # Apply pagination
                start_idx = (page - 1) * page_size
                end_idx = min(start_idx + page_size, len(all_recs))
                paged_recs = all_recs[start_idx:end_idx]
                
                # Convert internal indices to external IDs
                recommendations = []
                for post_idx, score in paged_recs:
                    post_id = self.reverse_post_map[post_idx]
                    post_details = self._get_post_details(post_id)
                    recommendations.append({
                        "post_id": post_id,
                        "score": score,
                        "rank": len(recommendations) + 1 + start_idx,
                        "details": post_details
                    })
                
                # Create response
                response = {
                    "mood_id": mood_id,
                    "page": page,
                    "page_size": page_size,
                    "total_items": len(all_recs),
                    "recommendations": recommendations
                }
                
                # Cache the results
                self.recommendation_cache[cache_key] = {
                    "timestamp": time.time(),
                    "recommendations": response
                }
                
                return response
        except Exception as e:
            logger.error(f"Error generating mood-based recommendations: {str(e)}")
            raise
    
    def _filter_by_category(self, recommendations, category_id):
        filtered_recs = []
        for post_idx, score in recommendations:
            post_category = int(self.data["post"].x[post_idx, 0].item())
            if post_category == category_id:
                filtered_recs.append((post_idx, score))
        return filtered_recs
    
    def _get_user_id_by_username(self, username):
        # Query the database for the user ID
        from app.models.database import neo4j_db
        query = "MATCH (u:User {username: $username}) RETURN u.id AS user_id"
        result = neo4j_db.run_query(query, {"username": username})
        if result and len(result) > 0 and "user_id" in result[0]:
            return str(result[0]["user_id"])
        return None
    
    # THIS IS THE MISSING METHOD - Added as a class method
    def _get_post_details(self, post_id):
        # Call the get_post_title_and_category method
        result = self.get_post_title_and_category(post_id)
        if result.get('success'):
            return {
                "title": result.get('title'),
                "category": result.get('category_name')
            }
        return {
            "title": f"Post {post_id}",
            "category": "Unknown"
        }
    
    # Fixed function moved as a class method
    def get_post_title_and_category(self, post_id):
        """
        Fetches post title and category name by post ID, going through all available pages if needed
        
        Args:
            post_id (int): The ID of the post to fetch
            
        Returns:
            dict: Object containing success status, title and category name or error message
        """
        try:
            # API endpoint
            api_url = 'https://api.socialverseapp.com/posts/summary/get'
            
            # Authentication token
            auth_token = 'flic_11d3da28e403d182c36a3530453e290add87d0b4a40ee50f17611f180d47956f'
            
            # Headers for the request
            headers = {
                'Flic-Token': auth_token,
                'Content-Type': 'application/json'
            }
            
            # Initialize pagination variables
            page = 1
            while True:
                # Make API request with pagination and page size of 1000
                response = requests.get(api_url, headers=headers, params={'page': page, 'page_size': 1000})
                
                # Check if response is OK
                response.raise_for_status()
                
                # Parse response data
                data = response.json()
                
                # Debug: Print the response data to inspect structure
                logger.debug(f"Page {page} data: {data}")
                
                # Check if request was successful
                if data.get('status') != 'success':
                    return {
                        'success': False,
                        'message': 'API returned unsuccessful status'
                    }
                
                # If no posts in response, stop loading more pages
                posts = data.get('posts', [])
                if not posts:
                    break  # No more posts available
                
                # Find the post with matching ID
                post = next((post for post in posts if post.get('id') == post_id), None)
                
                # If post is found, return title and category name
                if post:
                    title = post.get('title', 'No title available')
                    category_name = post.get('category', {}).get('name', 'No category available')
                    return {
                        'success': True,
                        'title': title,
                        'category_name': category_name
                    }
                
                # Increment the page number for the next request
                page += 1
            
            # If post is not found after checking all pages
            return {
                'success': False,
                'message': f'Post with ID {post_id} not found'
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"API request error: {str(e)}")
            return {
                'success': False,
                'message': f'Error fetching post: {str(e)}'
            }
        except Exception as e:
            logger.error(f"Unexpected error in get_post_title_and_category: {str(e)}")
            return {
                'success': False,
                'message': f'Unexpected error: {str(e)}'
            }


# Create singleton instance
recommendation_system = RecommendationSystem()