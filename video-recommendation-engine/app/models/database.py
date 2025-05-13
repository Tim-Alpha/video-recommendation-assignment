from neo4j import GraphDatabase
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

class Neo4jDatabase:
    def __init__(self):
        self._driver = None
        self._connect()
    
    def _connect(self):
        try:
            self._driver = GraphDatabase.driver(
                settings.NEO4J_URI,
                auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD)
            )
            logger.info("Connected to Neo4j database")
        except Exception as e:
            logger.error(f"Failed to connect to Neo4j: {str(e)}")
            raise
    
    def close(self):
        if self._driver:
            self._driver.close()
            logger.info("Neo4j connection closed")
    
    def run_query(self, query, params=None):
        with self._driver.session() as session:
            result = session.run(query, params or {})
            return result.data()
    
    def get_user_by_username(self, username):
        query = """
        MATCH (u:User {username: $username})
        RETURN u.id AS id, u.username AS username, u.first_name AS first_name, 
               u.last_name AS last_name, u.email AS email, u.bio AS bio,
               u.created_at AS created_at, u.updated_at AS updated_at
        """
        result = self.run_query(query, {"username": username})
        return result[0] if result else None
    
    def get_user_interactions(self, user_id):
        query = """
        MATCH (u:User {id: $user_id})-[r:INTERACTED]->(p:Post)
        RETURN p.id AS post_id, p.title AS title, r.type AS interaction_type, 
               r.weight AS weight, r.timestamp AS timestamp, r.strength AS strength
        ORDER BY r.timestamp DESC
        """
        return self.run_query(query, {"user_id": user_id})
    
    def get_category_posts(self, category_id):
        query = """
        MATCH (p:Post)
        WHERE p.category_id = $category_id
        RETURN p.id AS id, p.title AS title, p.content AS content,
               p.category_id AS category_id, p.category_name AS category_name,
               p.created_at AS created_at, p.updated_at AS updated_at
        """
        return self.run_query(query, {"category_id": category_id})
    
    def get_all_users(self):
        query = """
        MATCH (u:User)
        RETURN u.id AS id, u.username AS username, u.first_name AS first_name,
               u.last_name AS last_name
        """
        return self.run_query(query)
    
    def get_all_posts(self):
        query = """
        MATCH (p:Post)
        RETURN p.id AS id, p.title AS title, p.category_id AS category_id,
               p.category_name AS category_name, p.created_at AS created_at
        """
        return self.run_query(query)

    def get_post_by_id(self, post_id):
        
        post_id = int(post_id)  # Ensure post_id is an integer
        query = """
        MATCH (p:Post {id: $post_id})
        RETURN    
            p.title AS title, 
            p.category_name AS category_name
        """
        result = self.run_query(query, {"post_id": post_id})
        return result[0] if result else None



# Create a singleton instance
neo4j_db = Neo4jDatabase()
