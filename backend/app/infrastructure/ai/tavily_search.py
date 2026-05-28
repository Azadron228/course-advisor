import logging
import httpx
import asyncio
from typing import List, Dict, Any, Optional
from app.core.config import settings
from app.infrastructure.ai.youtube_search import YouTubeSearch

logger = logging.getLogger(__name__)

class TavilySearch:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.TAVILY_API_KEY
        self.base_url = "https://api.tavily.com/search"

    async def search(self, query: str, search_depth: str = "basic", max_results: int = 5) -> List[Dict[str, Any]]:
        if not self.api_key:
            logger.warning("Tavily API key not found. Skipping search.")
            return []

        logger.info(f"Tavily Search: [query='{query}'], [depth={search_depth}], [max_results={max_results}]")

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
        Uses YouTube Data API for video materials if YOUTUBE_API_KEY is configured.
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
        
        # Determine the primary search language suffix
        lang_suffix = ""
        search_depth = "basic"
        
        if language == "ru":
            lang_suffix = " на русском языке (in Russian language)"
            search_depth = "advanced" # Use advanced for better localized results
        elif language == "kk":
            lang_suffix = " қазақ тілінде (in Kazakh language)"
            search_depth = "advanced"
        elif language != "en":
            lang_suffix = f" in {language} language"
            search_depth = "advanced"

        if len(target_languages) > 1:
            # Multi-language search: include target languages (e.g. for language learning)
            # but still prioritize the primary user language
            extra_langs = [l for l in target_languages if l != language]
            lang_str = " or ".join([f"in {l}" for l in extra_langs])
            search_query = f"{base_query}{lang_suffix} or {lang_str}"
            search_depth = "advanced"
        else:
            search_query = f"{base_query}{lang_suffix}"
            
        search_query += " -site:coursera.org -site:udemy.com -site:edx.org -site:skillshare.com"
        
        # Check if YouTube Data API is configured
        has_youtube_key = settings.YOUTUBE_API_KEY and settings.YOUTUBE_API_KEY != "your_youtube_api_key_here"

        if has_youtube_key:
            # Exclude youtube from Tavily search query
            tavily_query = search_query + " -site:youtube.com"
            video_limit = max(1, max_results // 2)
            article_limit = max_results - video_limit
            
            logger.info(f"Educational Material Search: Using YouTube Data API for videos and Tavily for articles.")
            logger.info(f"Tavily Query: '{tavily_query}', depth: {search_depth}, limit: {article_limit}")
            logger.info(f"YouTube Query: '{topic}', limit: {video_limit}")

            # Run searches in parallel
            youtube_client = YouTubeSearch()
            tavily_task = self.search(tavily_query, max_results=article_limit * 2, search_depth=search_depth)
            youtube_task = youtube_client.search_videos(topic, max_results=video_limit * 2, language=language)
            
            tavily_results, youtube_results = await asyncio.gather(tavily_task, youtube_task)
            
            articles = []
            for res in tavily_results:
                if "youtube.com" not in (res.get("url") or ""):
                    articles.append({
                        "title": res.get("title", "Educational Resource"),
                        "description": res.get("content", "")[:200] + "...",
                        "url": res.get("url"),
                        "type": "article"
                    })
                    if len(articles) == article_limit:
                        break

            videos = youtube_results[:video_limit]
            
            # Combine results, maintaining the target proportions if possible.
            # If we didn't get enough of one type, we fill from the other up to max_results.
            materials = []
            materials.extend(articles)
            materials.extend(videos)
            
            # If we don't have enough results in total, grab more from our pools
            if len(materials) < max_results:
                remaining_slots = max_results - len(materials)
                extra_articles = [a for a in tavily_results if "youtube.com" not in (a.get("url") or "")]
                extra_articles_formatted = []
                for res in extra_articles:
                    formatted = {
                        "title": res.get("title", "Educational Resource"),
                        "description": res.get("content", "")[:200] + "...",
                        "url": res.get("url"),
                        "type": "article"
                    }
                    if formatted not in materials:
                        extra_articles_formatted.append(formatted)
                
                extra_videos = [v for v in youtube_results if v not in materials]
                
                # First fill with extra articles, then extra videos
                for art in extra_articles_formatted:
                    if len(materials) < max_results:
                        materials.append(art)
                for vid in extra_videos:
                    if len(materials) < max_results:
                        materials.append(vid)

            return materials[:max_results]
        else:
            logger.info(f"Educational Material Search: Constructed query: '{search_query}', depth: {search_depth}")
            results = await self.search(search_query, max_results=max_results, search_depth=search_depth)
            
            materials = []
            for res in results:
                materials.append({
                    "title": res.get("title", "Educational Resource"),
                    "description": res.get("content", "")[:200] + "...",
                    "url": res.get("url"),
                    "type": "video" if "youtube.com" in (res.get("url") or "") else "article"
                })
            return materials
