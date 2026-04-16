import pytest
from backend.app.core.redis_chat import RedisChatHistory

@pytest.mark.asyncio
async def test_redis_chat_history():
    history = RedisChatHistory()
    user_id = "test_user@example.com"
    await history.clear_history(user_id)
    
    await history.add_message(user_id, "user", "Hello")
    await history.add_message(user_id, "assistant", "Hi there!")
    
    messages = await history.get_history(user_id)
    assert len(messages) == 2
    assert messages[0]["role"] == "user"
    assert messages[1]["content"] == "Hi there!"
    
    await history.clear_history(user_id)
    assert len(await history.get_history(user_id)) == 0
