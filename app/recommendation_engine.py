import numpy as np
import pandas as pd
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.models import User, Post, UserInteraction, Category, Topic
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import networkx as nx
from collections import defaultdict
import torch
import torch.nn as nn
import torch.nn.functional as F
from app.ml.gnn_model import ContentEmbeddingModel


class RecommendationEngine:
    def __init__(self):
        self.content_model = None
        self.tfidf_vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
        self.user_embeddings = {}
        self.post_embeddings = {}
        self.interaction_graph = nx.Graph()
        
    def _extract_content_features(self, post: Post) -> np.ndarray:
        """Extract features from post content"""
        features = []
        
        # Text features
        text_content = f"{post.title or ''} {' '.join(post.tags or [])}"
        if hasattr(self, 'tfidf_matrix') and self.tfidf_matrix is not None:
            # Use pre-computed TF-IDF
            pass
        else:
            features.extend([0] * 1000)  # Placeholder for TF-IDF
        
        # Numerical features
        features.extend([
            post.view_count or 0,
            post.upvote_count or 0,
            post.comment_count or 0,
            post.rating_count or 0,
            post.average_rating or 0,
            post.share_count or 0,
            post.bookmark_count or 0,
            post.exit_count or 0,
        ])
        
        # Categorical features (one-hot encoded)
        category_id = post.category_id or 0
        topic_id = post.topic_id or 0
        
        # Simple encoding for now
        features.extend([category_id, topic_id])
        
        return np.array(features, dtype=np.float32)
    
    def _build_interaction_graph(self, db: Session):
        """Build user-post interaction graph"""
        self.interaction_graph.clear()
        
        # Get all interactions
        interactions = db.query(UserInteraction).all()
        
        for interaction in interactions:
            user_id = f"user_{interaction.user_id}"
            post_id = f"post_{interaction.post_id}"
            
            # Add nodes
            self.interaction_graph.add_node(user_id, type='user')
            self.interaction_graph.add_node(post_id, type='post')
            
            # Add edge with weight based on interaction type
            weight = self._get_interaction_weight(interaction.interaction_type)
            if interaction.rating_value:
                weight *= (interaction.rating_value / 100.0)  # Normalize rating
            
            self.interaction_graph.add_edge(user_id, post_id, weight=weight)
    
    def _get_interaction_weight(self, interaction_type: str) -> float:
        """Get weight for different interaction types"""
        weights = {
            'view': 1.0,
            'like': 3.0,
            'inspire': 5.0,
            'rate': 4.0,
            'bookmark': 2.0
        }
        return weights.get(interaction_type, 1.0)
    
    def _train_content_model(self, db: Session):
        """Train content embedding model"""
        posts = db.query(Post).all()
        
        if not posts:
            return
        
        # Extract features for all posts
        features_list = []
        for post in posts:
            features = self._extract_content_features(post)
            features_list.append(features)
        
        features_matrix = np.array(features_list)
        
        # Initialize and train model
        input_dim = features_matrix.shape[1]
        self.content_model = ContentEmbeddingModel(input_dim)
        
        # Simple training (in production, you'd use proper training loop)
        with torch.no_grad():
            features_tensor = torch.FloatTensor(features_matrix)
            embeddings = self.content_model(features_tensor)
            
            # Store embeddings
            for i, post in enumerate(posts):
                self.post_embeddings[post.id] = embeddings[i].numpy()
    
    def _get_user_embedding(self, db: Session, user_id: int) -> np.ndarray:
        """Get user embedding based on their interactions"""
        if user_id in self.user_embeddings:
            return self.user_embeddings[user_id]
        
        # Get user's interactions
        interactions = db.query(UserInteraction).filter(
            UserInteraction.user_id == user_id
        ).all()
        
        if not interactions:
            # Cold start: return average post embedding
            if self.post_embeddings:
                avg_embedding = np.mean(list(self.post_embeddings.values()), axis=0)
                self.user_embeddings[user_id] = avg_embedding
                return avg_embedding
            else:
                return np.zeros(64)  # Default embedding
        
        # Calculate weighted average of interacted post embeddings
        weighted_embeddings = []
        weights = []
        
        for interaction in interactions:
            if interaction.post_id in self.post_embeddings:
                embedding = self.post_embeddings[interaction.post_id]
                weight = self._get_interaction_weight(interaction.interaction_type)
                
                if interaction.rating_value:
                    weight *= (interaction.rating_value / 100.0)
                
                weighted_embeddings.append(embedding * weight)
                weights.append(weight)
        
        if weighted_embeddings:
            user_embedding = np.average(weighted_embeddings, weights=weights, axis=0)
        else:
            user_embedding = np.zeros(64)
        
        self.user_embeddings[user_id] = user_embedding
        return user_embedding
    
    def _calculate_similarity(self, user_embedding: np.ndarray, post_embedding: np.ndarray) -> float:
        """Calculate cosine similarity between user and post embeddings"""
        return np.dot(user_embedding, post_embedding) / (
            np.linalg.norm(user_embedding) * np.linalg.norm(post_embedding) + 1e-8
        )
    
    def _get_collaborative_recommendations(self, db: Session, user_id: int, limit: int = 10) -> List[int]:
        """Get recommendations using collaborative filtering"""
        # Find similar users
        user_interactions = db.query(UserInteraction).filter(
            UserInteraction.user_id == user_id
        ).all()
        
        if not user_interactions:
            return []
        
        # Get posts this user has interacted with
        user_post_ids = {interaction.post_id for interaction in user_interactions}
        
        # Find users with similar interactions
        similar_users = defaultdict(int)
        for interaction in user_interactions:
            # Find other users who interacted with the same post
            similar_interactions = db.query(UserInteraction).filter(
                UserInteraction.post_id == interaction.post_id,
                UserInteraction.user_id != user_id
            ).all()
            
            for similar_interaction in similar_interactions:
                similar_users[similar_interaction.user_id] += 1
        
        # Get recommendations from similar users
        recommendations = defaultdict(float)
        for similar_user_id, similarity_score in sorted(similar_users.items(), key=lambda x: x[1], reverse=True)[:5]:
            similar_user_interactions = db.query(UserInteraction).filter(
                UserInteraction.user_id == similar_user_id
            ).all()
            
            for interaction in similar_user_interactions:
                if interaction.post_id not in user_post_ids:
                    recommendations[interaction.post_id] += similarity_score * self._get_interaction_weight(interaction.interaction_type)
        
        # Return top recommendations
        sorted_recommendations = sorted(recommendations.items(), key=lambda x: x[1], reverse=True)
        return [post_id for post_id, score in sorted_recommendations[:limit]]
    
    def get_personalized_recommendations(self, db: Session, username: str, limit: int = 10) -> List[Post]:
        """Get personalized recommendations for a user"""
        # Get user
        user = db.query(User).filter(User.username == username).first()
        if not user:
            return []
        
        # Build interaction graph and train model
        self._build_interaction_graph(db)
        self._train_content_model(db)
        
        # Get user embedding
        user_embedding = self._get_user_embedding(db, user.id)
        
        # Get all available posts
        available_posts = db.query(Post).filter(
            Post.is_available_in_public_feed == True,
            Post.is_locked == False
        ).all()
        
        # Calculate scores for each post
        post_scores = []
        for post in available_posts:
            if post.id in self.post_embeddings:
                # Content-based similarity
                content_score = self._calculate_similarity(user_embedding, self.post_embeddings[post.id])
                
                # Popularity score
                popularity_score = (
                    (post.view_count or 0) * 0.1 +
                    (post.upvote_count or 0) * 0.3 +
                    (post.average_rating or 0) * 0.2 +
                    (post.share_count or 0) * 0.4
                ) / 1000.0  # Normalize
                
                # Combined score
                final_score = content_score * 0.7 + popularity_score * 0.3
                post_scores.append((post, final_score))
        
        # Sort by score and return top recommendations
        post_scores.sort(key=lambda x: x[1], reverse=True)
        return [post for post, score in post_scores[:limit]]
    
    def get_category_recommendations(self, db: Session, username: str, project_code: str, limit: int = 10) -> List[Post]:
        """Get category-specific recommendations"""
        # Get user
        user = db.query(User).filter(User.username == username).first()
        if not user:
            return []
        
        # Get posts from specific project/category
        category_posts = db.query(Post).join(Topic).filter(
            Topic.project_code == project_code,
            Post.is_available_in_public_feed == True,
            Post.is_locked == False
        ).all()
        
        if not category_posts:
            return []
        
        # Build interaction graph and train model
        self._build_interaction_graph(db)
        self._train_content_model(db)
        
        # Get user embedding
        user_embedding = self._get_user_embedding(db, user.id)
        
        # Calculate scores for category posts
        post_scores = []
        for post in category_posts:
            if post.id in self.post_embeddings:
                content_score = self._calculate_similarity(user_embedding, self.post_embeddings[post.id])
                popularity_score = (
                    (post.view_count or 0) * 0.1 +
                    (post.upvote_count or 0) * 0.3 +
                    (post.average_rating or 0) * 0.2 +
                    (post.share_count or 0) * 0.4
                ) / 1000.0
                
                final_score = content_score * 0.7 + popularity_score * 0.3
                post_scores.append((post, final_score))
        
        # Sort by score and return top recommendations
        post_scores.sort(key=lambda x: x[1], reverse=True)
        return [post for post, score in post_scores[:limit]]
    
    def get_cold_start_recommendations(self, db: Session, limit: int = 10) -> List[Post]:
        """Get recommendations for new users (cold start)"""
        # Return most popular posts
        popular_posts = db.query(Post).filter(
            Post.is_available_in_public_feed == True,
            Post.is_locked == False
        ).order_by(
            Post.view_count.desc(),
            Post.upvote_count.desc(),
            Post.average_rating.desc()
        ).limit(limit).all()
        
        return popular_posts


# Create global instance
recommendation_engine = RecommendationEngine() 