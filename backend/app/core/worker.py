from arq.connections import RedisSettings
from ..core.config import settings

# Import tasks
from ..tasks import run_hybrid_recommendation

redis_settings = RedisSettings.from_dsn(settings.REDIS_URL)


class WorkerSettings:
    functions = [run_hybrid_recommendation]
    redis_settings = redis_settings
