import json
from typing import List, Dict
from arq.connections import RedisSettings
from redis.asyncio import Redis
from ..core.config import settings

class RedisChatHistory:
    def __init__(self, redis_url: str = settings.REDIS_URL):
        self.redis = Redis.from_url(redis_url, decode_responses=True)
        self.prefix = "chat_history:"
        self.max_messages = 20

    async def add_message(self, user_id: str, role: str, content: str):
        key = f"{self.prefix}{user_id}"
        message = json.dumps({"role": role, "content": content})
        await self.redis.rpush(key, message)
        await self.redis.ltrim(key, -self.max_messages, -1)
        await self.redis.expire(key, 86400) # 24 hours

    async def get_history(self, user_id: str) -> List[Dict[str, str]]:
        key = f"{self.prefix}{user_id}"
        messages = await self.redis.lrange(key, 0, -1)
        return [json.loads(m) for m in messages]

    async def clear_history(self, user_id: str):
        key = f"{self.prefix}{user_id}"
        await self.redis.delete(key)
