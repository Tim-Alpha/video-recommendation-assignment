import os
from pydantic import BaseSettings
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Video Recommendation Engine"
    
    # API credentials
    FLIC_TOKEN: str = os.getenv("FLIC_TOKEN", "flic_11d3da28e403d182c36a3530453e290add87d0b4a40ee50f17611f180d47956f")
    API_BASE_URL: str = os.getenv("API_BASE_URL", "https://api.socialverseapp.com")
    
    # Neo4j settings
    NEO4J_URI: str = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    NEO4J_USER: str = os.getenv("NEO4J_USER", "neo4j")
    NEO4J_PASSWORD: str = os.getenv("NEO4J_PASSWORD", "Abhay31kashyap$$31")
    
    # Model settings
    MODEL_PATH: str = os.getenv("MODEL_PATH", "model.pth")
    DATA_PATH: str = os.getenv("DATA_PATH", "data/social_network_data.pt")
    
    # Cache settings
    CACHE_TTL: int = int(os.getenv("CACHE_TTL", "3600"))  # 1 hour
    
    class Config:
        case_sensitive = True

settings = Settings()
