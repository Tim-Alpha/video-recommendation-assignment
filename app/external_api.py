import httpx
from typing import List, Dict, Any, Optional
from config import settings
import asyncio
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)


class ExternalAPIClient:
    def __init__(self):
        self.base_url = settings.api_base_url
        self.headers = {
            "Flic-Token": settings.flic_token,
            "Content-Type": "application/json"
        }
    
    async def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """Make HTTP request to external API"""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{self.base_url}{endpoint}",
                    headers=self.headers,
                    params=params,
                    timeout=30.0
                )
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as e:
                logging.error(f"HTTP error occurred: {e}")
                return {"status": False, "error": str(e)}
            except Exception as e:
                logging.error(f"Error occurred: {e}")
                return {"status": False, "error": str(e)}
    
    async def get_all_posts(self, page: int = 1, page_size: int = 1000) -> Dict[str, Any]:
        """Get all posts from external API"""
        endpoint = "/posts/summary/get"
        params = {"page": page, "page_size": page_size}
        return await self._make_request(endpoint, params)
    
    async def get_all_users(self, page: int = 1, page_size: int = 1000) -> Dict[str, Any]:
        """Get all users from external API"""
        endpoint = "/users/get_all"
        params = {"page": page, "page_size": page_size}
        return await self._make_request(endpoint, params)
    
    async def get_viewed_posts(self, page: int = 1, page_size: int = 1000) -> Dict[str, Any]:
        """Get viewed posts from external API"""
        endpoint = "/posts/view"
        params = {
            "page": page, 
            "page_size": page_size,
            "resonance_algorithm": "resonance_algorithm_cjsvervb7dbhss8bdrj89s44jfjdbsjd0xnjkbvuire8zcjwerui3njfbvsujc5if"
        }
        return await self._make_request(endpoint, params)
    
    async def get_liked_posts(self, page: int = 1, page_size: int = 1000) -> Dict[str, Any]:
        """Get liked posts from external API"""
        endpoint = "/posts/like"
        params = {
            "page": page, 
            "page_size": page_size,
            "resonance_algorithm": "resonance_algorithm_cjsvervb7dbhss8bdrj89s44jfjdbsjd0xnjkbvuire8zcjwerui3njfbvsujc5if"
        }
        return await self._make_request(endpoint, params)
    
    async def get_inspired_posts(self, page: int = 1, page_size: int = 1000) -> Dict[str, Any]:
        """Get inspired posts from external API"""
        endpoint = "/posts/inspire"
        params = {
            "page": page, 
            "page_size": page_size,
            "resonance_algorithm": "resonance_algorithm_cjsvervb7dbhss8bdrj89s44jfjdbsjd0xnjkbvuire8zcjwerui3njfbvsujc5if"
        }
        return await self._make_request(endpoint, params)
    
    async def get_rated_posts(self, page: int = 1, page_size: int = 1000) -> Dict[str, Any]:
        """Get rated posts from external API"""
        endpoint = "/posts/rating"
        params = {
            "page": page, 
            "page_size": page_size,
            "resonance_algorithm": "resonance_algorithm_cjsvervb7dbhss8bdrj89s44jfjdbsjd0xnjkbvuire8zcjwerui3njfbvsujc5if"
        }
        return await self._make_request(endpoint, params)
    
    async def fetch_all_data(self) -> Dict[str, Any]:
        """Fetch all data from external APIs"""
        tasks = [
            self.get_all_posts(),
            self.get_all_users(),
            self.get_viewed_posts(),
            self.get_liked_posts(),
            self.get_inspired_posts(),
            self.get_rated_posts()
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        return {
            "posts": results[0],
            "users": results[1],
            "viewed_posts": results[2],
            "liked_posts": results[3],
            "inspired_posts": results[4],
            "rated_posts": results[5]
        }


# Create global instance
external_api = ExternalAPIClient() 