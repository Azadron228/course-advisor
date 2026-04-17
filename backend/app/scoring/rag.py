import logging
import asyncio
import os
from sqlalchemy.orm import Session
from ..api.v1.schemas.recommendations import ModelProvider, Student
from ..dtos.course import CourseDTO as Course
from ..agent import AgentRecommendation
from arq import create_pool
from arq.connections import RedisSettings
from arq.jobs import JobStatus
from ..core.config import settings

logger = logging.getLogger(__name__)

class RAGScorer:
    async def score(self, db: Session, student: Student, course: Course, provider: ModelProvider = ModelProvider.AUTO) -> AgentRecommendation:
        # Requirement: Wrap all agent.run() calls in ARQ jobs
        pool = await create_pool(RedisSettings.from_dsn(settings.REDIS_URL))
        
        job = await pool.enqueue_job(
            'run_agent_task',
            student.model_dump(),
            course.model_dump(),
            provider.value
        )
        if job is None:
            await pool.close()
            raise Exception("Failed to enqueue agent job.")
            
        # Poll for completion
        while True:
            status = await job.status()
            if status == JobStatus.complete:
                break
            elif status == JobStatus.not_found:
                logger.error(f"Agent job {job.job_id} failed or not found.")
                await pool.close()
                raise Exception(f"Agent job {job.job_id} failed.")
            await asyncio.sleep(0.5)
            
        result = await job.result()
        await pool.close()
        
        if isinstance(result, dict) and "error" in result:
             logger.error(f"Agent job failed with {result.get('error_type', 'Exception')}: {result['error']}")
             raise Exception(f"Agent recommendation failed: {result['error']}")
             
        return AgentRecommendation(**result)
