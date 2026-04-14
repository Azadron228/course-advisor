import logging
import asyncio
import os
import redis
from rq import Queue
from sqlalchemy.orm import Session
from ..schemas.internal import ModelProvider
from ..schemas.course import Student, Course
from ..schemas.recommendation import RecommendationResult # Not actually used here but for reference
from ..agent import AgentRecommendation

logger = logging.getLogger(__name__)

# Redis for enqueuing from the app
redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
redis_conn = redis.from_url(redis_url)
q = Queue(connection=redis_conn)

class RAGScorer:
    async def score(self, db: Session, student: Student, course: Course, provider: ModelProvider = ModelProvider.AUTO) -> AgentRecommendation:
        # Requirement: Wrap all agent.run() calls in RQ jobs
        from ..tasks import run_agent_task
        
        job = q.enqueue(
            run_agent_task,
            student.model_dump(),
            course.model_dump(),
            provider.value
        )
        
        # Poll for completion
        while not job.is_finished and not job.is_failed:
            await asyncio.sleep(0.5)
            
        if job.is_failed:
            logger.error(f"Agent job {job.get_id()} failed.")
            raise Exception(f"Agent job {job.get_id()} failed.")
            
        return AgentRecommendation(**job.result)
