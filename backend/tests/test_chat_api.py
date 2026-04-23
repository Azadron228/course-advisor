import os
os.environ["TESTING"] = "1"

import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.api.deps import get_current_active_user
from backend.app.schemas.user import UserBase

from unittest.mock import patch, AsyncMock

client = TestClient(app)

# Mock user
mock_user = UserBase(email="test@example.com", full_name="Test User", is_active=True)

def override_get_current_active_user():
    return mock_user

app.dependency_overrides[get_current_active_user] = override_get_current_active_user

@patch("backend.app.api.v1.recommendations.chat_history", spec=True)
@patch("backend.app.api.v1.recommendations.get_advisor_agent")
def test_chat_endpoint(mock_get_agent, mock_chat_history):
    # Setup mock agent
    mock_agent = AsyncMock()
    mock_agent.run = AsyncMock(return_value="I am your advisor. You said: Hello advisor")
    mock_get_agent.return_value = mock_agent
    
    # Setup mock history
    mock_chat_history.add_message = AsyncMock()
    mock_chat_history.get_history = AsyncMock(return_value=[
        {"role": "user", "content": "Hello advisor"},
        {"role": "assistant", "content": "I am your advisor. You said: Hello advisor"}
    ])
    
    response = client.post(
        "/api/v1/recommendations/chat",
        json={"message": "Hello advisor"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "response" in data
    assert "history" in data
    assert data["response"] == "I am your advisor. You said: Hello advisor"
    assert len(data["history"]) == 2
    assert data["history"][0]["role"] == "user"

@patch("backend.app.api.v1.recommendations.chat_history", spec=True)
def test_get_chat_history(mock_chat_history):
    # Setup mock
    mock_chat_history.get_history = AsyncMock(return_value=[
        {"role": "user", "content": "Hello advisor"},
        {"role": "assistant", "content": "I am your advisor. You said: Hello advisor"}
    ])
    
    response = client.get("/api/v1/recommendations/chat/history")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 2
    assert data[0]["role"] == "user"
