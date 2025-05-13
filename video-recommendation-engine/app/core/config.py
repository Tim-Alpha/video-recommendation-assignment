import os
from pydantic import BaseSettings
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings(BaseSettings):
    API_V1_STR: str
    PROJECT_NAME: str
    
    # API credentials
    FLIC_TOKEN: str
    API_BASE_URL: str
    
    # Neo4j settings
    NEO4J_URI: str
    NEO4J_USER: str
    NEO4J_PASSWORD: str
    
    # Model settings
    MODEL_PATH: str
    DATA_PATH: str
    
    # Cache settings
    CACHE_TTL: int
    
    class Config:
        case_sensitive = True

# Initialize settings from environment variables
settings = Settings()
