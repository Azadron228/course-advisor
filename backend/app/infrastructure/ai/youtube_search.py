import logging
import httpx
import html
from typing import List, Dict, Any, Optional
from app.core.config import settings

logger = logging.getLogger(__name__)

class YouTubeSearch:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.YOUTUBE_API_KEY
        self.base_url = "https://www.googleapis.com/youtube/v3/search"

    async def search_videos(self, query: str, max_results: int = 5, language: str = "en") -> List[Dict[str, Any]]:
        """
        Search for videos on YouTube using the YouTube Data API v3.
        """
        if not self.api_key or self.api_key == "your_youtube_api_key_here":
            logger.warning("YouTube API key not found or not configured. Skipping YouTube search.")
            return []

        logger.info(f"YouTube Search: [query='{query}'], [max_results={max_results}], [language={language}]")

        params = {
            "key": self.api_key,
            "q": query,
            "part": "snippet",
            "type": "video",
            "maxResults": max_results,
        }

        # Mapping common language codes for relevance language if helpful
        if language:
            params["relevanceLanguage"] = language

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(self.base_url, params=params, timeout=15.0)
                if response.status_code != 200:
                    logger.error(f"YouTube search API error: {response.status_code} - {response.text}")
                    return []
                
                data = response.json()
                items = data.get("items", [])
                
                materials = []
                for item in items:
                    video_id = item.get("id", {}).get("videoId")
                    if not video_id:
                        continue
                        
                    snippet = item.get("snippet", {})
                    raw_title = snippet.get("title", "YouTube Video")
                    raw_description = snippet.get("description", "")
                    
                    # Unescape HTML entities from YouTube API
                    title = html.unescape(raw_title)
                    description = html.unescape(raw_description)
                    
                    materials.append({
                        "title": title,
                        "description": description[:200] + "..." if len(description) > 200 else description,
                        "url": f"https://www.youtube.com/watch?v={video_id}",
                        "type": "video"
                    })
                return materials
        except Exception as e:
            logger.error(f"YouTube search failed for query '{query}': {e}")
            return []
