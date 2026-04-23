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


@pytest.mark.asyncio
async def test_redis_chat_history_limit():
    history = RedisChatHistory()
    user_id = "test_user_limit@example.com"
    await history.clear_history(user_id)

    # Add more than max_messages (20)
    for i in range(25):
        await history.add_message(user_id, "user", f"Message {i}")

    messages = await history.get_history(user_id)
    assert len(messages) == 20
    assert messages[0]["content"] == "Message 5"
    assert messages[19]["content"] == "Message 24"

    await history.clear_history(user_id)
