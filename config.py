from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # API Configuration
    flic_token: str = "flic_11d3da28e403d182c36a3530453e290add87d0b4a40ee50f17611f180d47956f"
    api_base_url: str = "https://api.socialverseapp.com"
    
    # Database Configuration
    database_url: str = "sqlite:///./video_recommendation.db"
    
    # App Configuration
    app_name: str = "Video Recommendation Engine"
    debug: bool = True
    
    class Config:
        env_file = ".env"


settings = Settings() 