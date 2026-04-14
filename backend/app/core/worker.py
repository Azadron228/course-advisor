from arq.connections import RedisSettings
from ..core.config import settings

# Import tasks
from ..jobs import run_hybrid_recommendation
from ..tasks import run_agent_task

redis_settings = RedisSettings.from_dsn(settings.REDIS_URL)

class WorkerSettings:
    functions = [run_hybrid_recommendation, run_agent_task]
    redis_settings = redis_settings
