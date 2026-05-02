import logging
from app.domain.recommendation.entities import Student, ModelProvider
from app.domain.catalog.entities import Course
from app.infrastructure.ai.agent import (
    get_recommendation_agent,
    get_model,
    parse_agent_recommendation,
)

from app.infrastructure.ai.embeddings import get_embedding, chunk_text
from app.infrastructure.db.models import CourseMaterialORM, CourseMaterialChunkORM, CourseORM
from sqlalchemy import update
from app.infrastructure.db.session import SessionLocal

logger = logging.getLogger(__name__)


async def process_material_embeddings(ctx: dict, material_id: int) -> dict:
    logger.info(f"Starting embedding generation for material {material_id}")
    
    # We use a context manager for the session to ensure it's closed
    with SessionLocal() as session:
        try:
            material = session.get(CourseMaterialORM, material_id)
            if not material:
                logger.error(f"Material {material_id} not found")
                return {"error": "Material not found"}

            # 1. Chunking
            text_chunks = chunk_text(material.content)
            total = len(text_chunks)
            
            # Update material status and total chunks
            session.execute(
                update(CourseMaterialORM)
                .where(CourseMaterialORM.id == material_id)
                .values(total_chunks=total, status="processing")
            )
            session.commit()

            # 2. Embedding each chunk
            for i, chunk_txt in enumerate(text_chunks):
                emb = get_embedding(chunk_txt)
                chunk_orm = CourseMaterialChunkORM(
                    material_id=material_id,
                    content=chunk_txt,
                    embedding=emb,
                    chunk_index=i
                )
                session.add(chunk_orm)
                
                # Update progress
                session.execute(
                    update(CourseMaterialORM)
                    .where(CourseMaterialORM.id == material_id)
                    .values(processed_chunks=i + 1)
                )
                session.commit()
                logger.debug(f"Processed chunk {i+1}/{total} for material {material_id}")

            # 3. Finalize
            session.execute(
                update(CourseMaterialORM)
                .where(CourseMaterialORM.id == material_id)
                .values(status="analyzed")
            )
            
            # Also update course embedding (only uses description now)
            course = session.get(CourseORM, material.course_id)
            if course:
                new_course_emb = get_embedding(course.description)
                course.embedding = new_course_emb
            
            session.commit()
            logger.info(f"Successfully processed material {material_id}")
            return {"status": "success", "chunks": total}

        except Exception as e:
            logger.error(f"Error processing material {material_id}: {e}", exc_info=True)
            session.execute(
                update(CourseMaterialORM)
                .where(CourseMaterialORM.id == material_id)
                .values(status="error")
            )
            session.commit()
            return {"error": str(e)}


async def run_agent_task(
    ctx: dict, student_dict: dict, course_dict: dict, provider_name: str
) -> dict:
    try:
        # Convert dicts back to domain entities
        student = Student(**student_dict)
        course = Course(**course_dict)
        provider = ModelProvider(provider_name)

        llm = get_model(provider)
        agent = get_recommendation_agent(llm, student, course)

        handler = agent.run(
            user_msg="Evaluate how well this course fits the student and provide your recommendation in JSON format."
        )
        response = await handler
        
        from llama_index.core.agent.workflow.workflow_events import AgentOutput
        response_content = str(response.response) if isinstance(response, AgentOutput) else str(response)

        result = parse_agent_recommendation(response_content)
        # Return as dict for serialization
        return {"score": result.score, "reasoning": result.reasoning, "tags": result.tags}
    except Exception as e:
        logger.error(f"Error in run_agent_task: {e}", exc_info=True)
        return {"error": str(e), "error_type": type(e).__name__, "status": "failed"}


async def run_hybrid_recommendation(
    ctx: dict, student_dict: dict, preference_dict: dict, provider_name: str = "auto"
) -> dict:
    from app.core.container import get_container
    from app.services.advisor_service import AdvisorService
    from app.domain.recommendation.entities import UserPreference, TranscriptEntry
    from app.api.v1.schemas.recommendations import RecommendationResponse

    try:
        transcript = [
            TranscriptEntry(**entry) for entry in student_dict.get("transcript", [])
        ]
        student = Student(
            id=student_dict["id"],
            name=student_dict["name"],
            transcript=transcript,
            current_skills=student_dict["current_skills"],
        )
        preference = UserPreference(**preference_dict)
        provider = ModelProvider(provider_name)

        container = get_container()
        advisor_service = container.resolve(AdvisorService)
        courses = advisor_service.course_repo.get_all()

        domain_response = await advisor_service.recommend(
            student, courses, preference, provider=provider
        )

        schema_response = RecommendationResponse.model_validate(domain_response)
        return schema_response.model_dump()
    except Exception as e:
        logger.error(f"Error in run_hybrid_recommendation task: {e}", exc_info=True)
        return {"error": str(e), "error_type": type(e).__name__, "status": "failed"}
