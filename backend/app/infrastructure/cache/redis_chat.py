import json
import logging
from typing import List, Dict
from app.core.config import settings
from redis.asyncio import Redis

logger = logging.getLogger(__name__)


class RedisChatHistory:
    def __init__(self, redis_url: str = settings.REDIS_URL):
        self.redis = Redis.from_url(redis_url, decode_responses=True)
        self.prefix = "chat_history:"
        self.max_messages = getattr(settings, "REDIS_CHAT_MAX_MESSAGES", 20)
        self.expire_seconds = getattr(settings, "REDIS_CHAT_EXPIRE_SECONDS", 86400)

    async def add_message(self, user_id: str, role: str, content: str):
        if not user_id:
            logger.error("Attempted to add message with empty user_id")
            return

        try:
            key = f"{self.prefix}{user_id}"
            message = json.dumps({"role": role, "content": content})
            await self.redis.rpush(key, message)
            await self.redis.ltrim(key, -self.max_messages, -1)
            await self.redis.expire(key, self.expire_seconds)
        except Exception as e:
            logger.error(f"Error adding message to Redis for user {user_id}: {e}")

    async def get_history(self, user_id: str) -> List[Dict[str, str]]:
        if not user_id:
            return []

        try:
            key = f"{self.prefix}{user_id}"
            messages = await self.redis.lrange(key, 0, -1)
            history = []
            for m in messages:
                try:
                    history.append(json.loads(m))
                except json.JSONDecodeError:
                    logger.warning(f"Corrupted message found in Redis for user {user_id}")
            return history
        except Exception as e:
            logger.error(f"Error getting history from Redis for user {user_id}: {e}")
            return []

    async def clear_history(self, user_id: str):
        if not user_id:
            return

        try:
            key = f"{self.prefix}{user_id}"
            await self.redis.delete(key)
        except Exception as e:
            logger.error(f"Error clearing history from Redis for user {user_id}: {e}")
