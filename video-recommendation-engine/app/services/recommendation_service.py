from app.models.recommendation import recommendation_system
from app.models.database import neo4j_db
import logging

logger = logging.getLogger(__name__)

class RecommendationService:
    def __init__(self):
        self.recommendation_system = recommendation_system
        self.db = neo4j_db
    
    async def get_personalized_feed(self, username, page=1, page_size=10, project_code=None):
        try:
            # If project_code is provided, convert it to category_id
            category_id = None
            if project_code:
                category_id = self._get_category_id_from_project_code(project_code)
            
            # Get recommendations
            recommendations = self.recommendation_system.get_recommendations(
                username=username,
                page=page,
                page_size=page_size,
                category_id=category_id
            )
            
            # Enrich recommendations with database data
            enriched_recommendations = self._enrich_recommendations(recommendations)
            
            return enriched_recommendations
        except Exception as e:
            logger.error(f"Error getting personalized feed: {str(e)}")
            raise
    
    async def get_mood_based_feed(self, mood_id, page=1, page_size=10, project_code=None):
        try:
            # If project_code is provided, convert it to category_id
            category_id = None
            if project_code:
                category_id = self._get_category_id_from_project_code(project_code)
            
            # Get recommendations
            recommendations = self.recommendation_system.get_recommendations(
                username=None,  # None username triggers cold start
                page=page,
                page_size=page_size,
                category_id=category_id,
                mood_id=mood_id
            )
            
            # Enrich recommendations with database data
            enriched_recommendations = self._enrich_recommendations(recommendations)
            
            return enriched_recommendations
        except Exception as e:
            logger.error(f"Error getting mood-based feed: {str(e)}")
            raise
    
    def _get_category_id_from_project_code(self, project_code):
        # This would typically involve a database lookup
        # For now, use a simple mapping
        project_code_to_category = {
            "motivation": 1,
            "fitness": 2,
            "finance": 3,
            "mindfulness": 4
        }
        return project_code_to_category.get(project_code.lower())
    
    def _enrich_recommendations(self, recommendations):
        # Add additional information to recommendations from the database
        for rec in recommendations.get("recommendations", []):
            post_id = rec["post_id"]
            # Get additional post details from database
            post_details = self._get_post_details_from_db(post_id)
            if post_details:
                rec["details"].update(post_details)
        
        return recommendations
    
    def _get_post_details_from_db(self, post_id):
        # Get post details from Neo4j
        query = """
        MATCH (p:Post {id: $post_id})
        RETURN p.title AS title, p.category_id AS category_id,
               p.view_count AS view_count, p.upvote_count AS upvote_count
        """
        result = self.db.run_query(query, {"post_id": post_id})
        
        if result:
            return result[0]
        return {}

recommendation_service = RecommendationService()
