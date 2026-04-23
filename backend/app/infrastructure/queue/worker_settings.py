from arq.connections import RedisSettings
from app.core.config import settings
from app.tasks.recommendation_tasks import run_agent_task

# You can also add other tasks here
# from app.tasks.other_tasks import some_other_task

redis_settings = RedisSettings.from_dsn(settings.REDIS_URL)

class WorkerSettings:
    functions = [run_agent_task]
    redis_settings = redis_settings
