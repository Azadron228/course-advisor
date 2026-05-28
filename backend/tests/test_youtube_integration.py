import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from app.infrastructure.ai.youtube_search import YouTubeSearch
from app.infrastructure.ai.tavily_search import TavilySearch
from app.core.config import settings

@pytest.mark.asyncio
async def test_youtube_search_parsing():
    search_client = YouTubeSearch(api_key="fake_key")
    
    mock_response_data = {
        "items": [
            {
                "id": {"kind": "youtube#video", "videoId": "dQw4w9WgXcQ"},
                "snippet": {
                    "title": "Rick Astley &amp; Friends - Never Gonna Give You Up",
                    "description": "The official video for &#39;Never Gonna Give You Up&#39;.",
                }
            }
        ]
    }
    
    # Mock httpx AsyncClient
    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_response_data
        mock_get.return_value = mock_response
        
        results = await search_client.search_videos("rick astley", max_results=1)
        
        # Verify the request
        mock_get.assert_called_once()
        assert mock_get.call_args[1]["params"]["key"] == "fake_key"
        assert mock_get.call_args[1]["params"]["q"] == "rick astley"
        
        # Verify results parsing and HTML unescaping
        assert len(results) == 1
        assert results[0]["title"] == "Rick Astley & Friends - Never Gonna Give You Up"
        assert results[0]["description"] == "The official video for 'Never Gonna Give You Up'."
        assert results[0]["url"] == "https://www.youtube.com/watch?v={}".format("dQw4w9WgXcQ")
        assert results[0]["type"] == "video"

@pytest.mark.asyncio
async def test_youtube_search_handles_no_key():
    search_client = YouTubeSearch(api_key=None)
    with patch.object(settings, "YOUTUBE_API_KEY", None):
        results = await search_client.search_videos("test")
        assert results == []

@pytest.mark.asyncio
async def test_tavily_educational_materials_fallback():
    # Test when YouTube API key is missing
    tavily_client = TavilySearch(api_key="fake_tavily_key")
    
    mock_tavily_results = [
        {"title": "Intro to Python", "content": "Learn Python basics", "url": "https://python.org"},
        {"title": "Python Video Tutorial", "content": "Video tutorial on Python", "url": "https://youtube.com/watch?v=123"}
    ]
    
    with patch.object(settings, "YOUTUBE_API_KEY", None), \
         patch.object(tavily_client, "search", new_callable=AsyncMock) as mock_tavily_search:
        
        mock_tavily_search.return_value = mock_tavily_results
        
        results = await tavily_client.search_educational_materials("Python", max_results=2)
        
        # Verify it fallback to only tavily search
        mock_tavily_search.assert_called_once_with(
            "best Python official documentation, youtube tutorials, and technical articles -site:coursera.org -site:udemy.com -site:edx.org -site:skillshare.com",
            max_results=2,
            search_depth="basic"
        )
        
        assert len(results) == 2
        assert results[0]["type"] == "article"
        assert results[1]["type"] == "video"

@pytest.mark.asyncio
async def test_tavily_and_youtube_combined_search():
    # Test when YouTube API key is present
    tavily_client = TavilySearch(api_key="fake_tavily_key")
    
    mock_tavily_results = [
        {"title": "Python Docs", "content": "Official docs", "url": "https://docs.python.org"},
        {"title": "Real Python Article", "content": "Intermediate tutorial", "url": "https://realpython.com"}
    ]
    
    mock_youtube_results = [
        {
            "title": "Python for Beginners",
            "description": "Learn python in 1 hour",
            "url": "https://www.youtube.com/watch?v=beginner",
            "type": "video"
        }
    ]
    
    with patch.object(settings, "YOUTUBE_API_KEY", "valid_youtube_key"), \
         patch.object(tavily_client, "search", new_callable=AsyncMock) as mock_tavily_search, \
         patch("app.infrastructure.ai.youtube_search.YouTubeSearch.search_videos", new_callable=AsyncMock) as mock_youtube_search:
        
        mock_tavily_search.return_value = mock_tavily_results
        mock_youtube_search.return_value = mock_youtube_results
        
        # max_results is 3, so video_limit = 1, article_limit = 2
        results = await tavily_client.search_educational_materials("Python", max_results=3)
        
        # Verify both search engines were called
        mock_tavily_search.assert_called_once()
        assert " -site:youtube.com" in mock_tavily_search.call_args[0][0]
        
        mock_youtube_search.assert_called_once_with("Python", max_results=2, language="en")
        
        assert len(results) == 3
        # 2 articles + 1 video
        articles = [r for r in results if r["type"] == "article"]
        videos = [r for r in results if r["type"] == "video"]
        assert len(articles) == 2
        assert len(videos) == 1
        assert articles[0]["url"] == "https://docs.python.org"
        assert videos[0]["url"] == "https://www.youtube.com/watch?v=beginner"
