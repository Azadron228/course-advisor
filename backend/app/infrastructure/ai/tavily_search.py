import logging
import httpx
from typing import List, Dict, Any, Optional
from app.core.config import settings

logger = logging.getLogger(__name__)

class TavilySearch:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.TAVILY_API_KEY
        self.base_url = "https://api.tavily.com/search"

    async def search(self, query: str, search_depth: str = "basic", max_results: int = 5) -> List[Dict[str, Any]]:
        if not self.api_key:
            logger.warning("Tavily API key not found. Skipping search.")
            return []

        payload = {
            "api_key": self.api_key,
            "query": query,
            "search_depth": search_depth,
            "max_results": max_results,
            "include_answer": True,
            "include_raw_content": False,
            "include_images": False,
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(self.base_url, json=payload, timeout=30.0)
                if response.status_code != 200:
                    logger.error(f"Tavily search API error: {response.status_code} - {response.text}")
                    return []
                data = response.json()
                return data.get("results", [])
        except Exception as e:
            logger.error(f"Tavily search failed for query '{query}': {e}")
            return []

    async def get_search_context(self, query: str, max_results: int = 5) -> str:
        results = await self.search(query, max_results=max_results)
        if not results:
            return ""

        context = "Search results for context:\n\n"
        for i, res in enumerate(results):
            context += f"Result {i+1}:\n"
            context += f"Title: {res.get('title')}\n"
            context += f"Content: {res.get('content')}\n"
            context += f"URL: {res.get('url')}\n\n"
        
        return context

    async def search_educational_materials(self, topic: str, max_results: int = 5, language: str = "en") -> List[Dict[str, Any]]:
        """
        Search for high-quality educational materials (docs, tutorials, videos).
        Filters out common course platforms to focus on free/official resources.
        """
        # Common language detection in topic
        target_languages = []
        if language:
            target_languages.append(language)
            
        # Basic heuristic for language learning: if topic mentions a language, search in that language too
        lang_keywords = {
            "spanish": ["spanish", "español"],
            "french": ["french", "français"],
            "german": ["german", "deutsch"],
            "italian": ["italian", "italiano"],
            "russian": ["russian", "русский"],
            "kazakh": ["kazakh", "қазақ"],
            "chinese": ["chinese", "中文"],
            "japanese": ["japanese", "日本語"],
        }
        
        topic_lower = topic.lower()
        for lang_name, variations in lang_keywords.items():
            if any(v in topic_lower for v in variations):
                # Don't add if it's already the primary language
                if lang_name not in target_languages:
                    target_languages.append(lang_name)

        # Build query
        base_query = f"best {topic} official documentation, youtube tutorials, and technical articles"
        
        if len(target_languages) > 1:
            # Multi-language search
            lang_str = " or ".join([f"in {l}" for l in target_languages])
            search_query = f"{base_query} {lang_str}"
        elif language == "ru":
            search_query = f"{base_query} на русском языке"
        elif language == "kk":
            search_query = f"{base_query} қазақ тілінде"
        elif language != "en":
            search_query = f"{base_query} in {language} language"
        else:
            search_query = base_query
            
        search_query += " -site:coursera.org -site:udemy.com -site:edx.org -site:skillshare.com"
        
        results = await self.search(search_query, max_results=max_results)
        
        materials = []
        for res in results:
            materials.append({
                "title": res.get("title", "Educational Resource"),
                "description": res.get("content", "")[:200] + "...",
                "url": res.get("url"),
                "type": "video" if "youtube.com" in (res.get("url") or "") else "article"
            })
        return materials
