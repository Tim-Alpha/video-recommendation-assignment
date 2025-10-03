import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from database_manager import fetch_post_likes_ids, fetch_post_views_ids, fetch_post_inspires_ids, fetch_post_ratings_ids_and_rating, load_updated_post_summaries
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class RecommendationEngine:
    def __init__(self):
        self.likes_df = None
        self.views_df = None
        self.inspires_df = None
        self.ratings_df = None
        self.posts_df = None
        self.interaction_matrix = None
        self.user_similarity_df = None
        self.content_similarity_df = None

    def load_and_prepare_data(self):
        # Load data from database
        post_likes = fetch_post_likes_ids()['likes']
        post_views = fetch_post_views_ids()['views']
        post_inspires = fetch_post_inspires_ids()['inspires']
        post_ratings = fetch_post_ratings_ids_and_rating()['ratings']
        updated_posts = load_updated_post_summaries()['posts']

        # Convert to DataFrames
        self.likes_df = pd.DataFrame(post_likes, columns=['user_id', 'post_id'])
        self.views_df = pd.DataFrame(post_views, columns=['user_id', 'post_id'])
        self.inspires_df = pd.DataFrame(post_inspires, columns=['user_id', 'post_id'])
        self.ratings_df = pd.DataFrame(post_ratings, columns=['user_id', 'post_id', 'rating_percent'])
        self.posts_df = pd.DataFrame(updated_posts)

        # Drop estimated_duration
        self.posts_df = self.posts_df.drop(columns=['estimated_duration'], errors='ignore')

        # Handle missing values and data types
        self.posts_df['summary'] = self.posts_df['summary'].fillna('').astype(str)
        self.posts_df['keywords'] = self.posts_df['keywords'].apply(
            lambda x: ' '.join(x) if isinstance(x, list) else str(x) if pd.notnull(x) else ''
        )
        self.posts_df['category'] = self.posts_df['category'].fillna('Unknown')

        # Combine summary and keywords for NLP
        self.posts_df['text_content'] = self.posts_df['summary'] + ' ' + self.posts_df['keywords']

        # Filter interactions to only include post_ids present in posts_df
        valid_post_ids = set(self.posts_df['post_id'])
        self.likes_df = self.likes_df[self.likes_df['post_id'].isin(valid_post_ids)]
        self.views_df = self.views_df[self.views_df['post_id'].isin(valid_post_ids)]
        self.inspires_df = self.inspires_df[self.inspires_df['post_id'].isin(valid_post_ids)]
        self.ratings_df = self.ratings_df[self.ratings_df['post_id'].isin(valid_post_ids)]

        # Log dropped interactions
        logging.info(f"Filtered likes: {len(post_likes) - len(self.likes_df)} interactions dropped")
        logging.info(f"Filtered views: {len(post_views) - len(self.views_df)} interactions dropped")
        logging.info(f"Filtered inspires: {len(post_inspires) - len(self.inspires_df)} interactions dropped")
        logging.info(f"Filtered ratings: {len(post_ratings) - len(self.ratings_df)} interactions dropped")

    def compute_content_similarity(self):
        # Initialize TF-IDF vectorizer
        tfidf = TfidfVectorizer(stop_words='english', max_features=5000)
        tfidf_matrix = tfidf.fit_transform(self.posts_df['text_content'])

        # Compute cosine similarity between posts
        content_similarity = cosine_similarity(tfidf_matrix)
        self.content_similarity_df = pd.DataFrame(content_similarity, index=self.posts_df['post_id'], columns=self.posts_df['post_id'])

    def build_interaction_matrix(self):
        # Create user-post interaction matrix
        all_users = set(self.likes_df['user_id']).union(self.views_df['user_id'], self.inspires_df['user_id'], self.ratings_df['user_id'])
        all_posts = set(self.posts_df['post_id'])
        
        # Initialize interaction matrix
        self.interaction_matrix = pd.DataFrame(0.0, index=list(all_users), columns=list(all_posts))

        # Assign weights to interactions
        LIKE_WEIGHT = 1.0
        VIEW_WEIGHT = 0.5
        INSPIRE_WEIGHT = 1.5
        RATING_THRESHOLD = 50  # Ratings above this are positive

        # Fill matrix with likes
        for _, row in self.likes_df.iterrows():
            self.interaction_matrix.loc[row['user_id'], row['post_id']] += LIKE_WEIGHT

        # Fill matrix with views
        for _, row in self.views_df.iterrows():
            self.interaction_matrix.loc[row['user_id'], row['post_id']] += VIEW_WEIGHT

        # Fill matrix with inspires
        for _, row in self.inspires_df.iterrows():
            self.interaction_matrix.loc[row['user_id'], row['post_id']] += INSPIRE_WEIGHT

        # Fill matrix with ratings (positive ratings only)
        for _, row in self.ratings_df.iterrows():
            if row['rating_percent'] > RATING_THRESHOLD:
                self.interaction_matrix.loc[row['user_id'], row['post_id']] += row['rating_percent'] / 100.0

    def compute_user_similarity(self):
        # Compute user-user similarity using cosine similarity
        user_similarity = cosine_similarity(self.interaction_matrix)
        self.user_similarity_df = pd.DataFrame(user_similarity, index=self.interaction_matrix.index, columns=self.interaction_matrix.index)

    def recommend_posts(self, user_id, category=None, num_recommendations=10):
        # Load and prepare data if not already done
        if self.posts_df is None:
            self.load_and_prepare_data()
            self.compute_content_similarity()
            self.build_interaction_matrix()
            self.compute_user_similarity()

        # Get posts the user has interacted with
        user_interactions = set(self.likes_df[self.likes_df['user_id'] == user_id]['post_id']).union(
            self.views_df[self.views_df['user_id'] == user_id]['post_id'],
            self.inspires_df[self.inspires_df['user_id'] == user_id]['post_id'],
            self.ratings_df[self.ratings_df['user_id'] == user_id]['post_id']
        )

        if user_id not in self.interaction_matrix.index or not user_interactions:
            logging.info(f"No interactions found for user {user_id}")
            return []

        # Collaborative filtering: Get similar users' preferences
        similar_users = self.user_similarity_df.loc[user_id].sort_values(ascending=False)[1:11]  # Top 10 similar users
        collab_scores = pd.Series(0.0, index=self.interaction_matrix.columns)
        for sim_user, similarity in similar_users.items():
            collab_scores += self.interaction_matrix.loc[sim_user] * similarity

        # Content-based filtering: Get similar posts to those the user liked/viewed/inspired/rated
        content_scores = pd.Series(0.0, index=self.posts_df['post_id'])
        for post_id in user_interactions:
            if post_id in self.content_similarity_df.index:
                content_scores += self.content_similarity_df.loc[post_id]

        # Combine scores (weight collaborative and content-based)
        final_scores = 0.6 * collab_scores + 0.4 * content_scores

        # Filter out posts the user has already interacted with
        final_scores = final_scores.drop(user_interactions, errors='ignore')

        # Apply category filter if specified
        if category:
            category_posts = self.posts_df[self.posts_df['category'] == category]['post_id']
            final_scores = final_scores[final_scores.index.isin(category_posts)]
            if final_scores.empty:
                logging.info(f"No posts found in category {category} for user {user_id}")
                return []

        # Boost posts in user's preferred categories
        user_categories = self.posts_df[self.posts_df['post_id'].isin(user_interactions)]['category'].value_counts().index[:3]
        category_boost = self.posts_df.set_index('post_id')['category'].map(
            lambda x: 1.2 if x in user_categories else 1.0
        )
        final_scores = final_scores * category_boost

        # Get top recommendations
        recommendations = final_scores.sort_values(ascending=False).head(num_recommendations).index.tolist()

        logging.info(f"Recommended {len(recommendations)} posts for user {user_id} in category {category}: {recommendations}")
        return recommendations if recommendations else []