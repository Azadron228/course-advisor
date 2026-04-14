import logging
from typing import List
from sqlalchemy.orm import Session
from ..schemas.course import Student, Course, UserPreference
from ..schemas.recommendation import (
    RecommendationResponse, RecommendationResult, ScoreBreakdown
)
from ..schemas.internal import ModelProvider
from ..scoring.content import ContentScorer
from ..scoring.skill_gap import SkillGapScorer
from ..scoring.rag import RAGScorer
from ..scoring.preference import PreferenceScorer

from ..analysis_agent import analysis_agent, AnalysisDeps, is_capable_model, parse_global_analysis, GlobalAnalysis
from ..agent import get_model

logger = logging.getLogger(__name__)

class HybridScorer:
    def __init__(self):
        self.content_scorer = ContentScorer()
        self.skill_gap_scorer = SkillGapScorer()
        self.rag_scorer = RAGScorer()
        self.preference_scorer = PreferenceScorer()
        
    async def recommend(
        self, 
        db: Session,
        student: Student, 
        courses: List[Course], 
        preference: UserPreference,
        provider: ModelProvider = ModelProvider.AUTO
    ) -> RecommendationResponse:
        results = []
        
        # 1. Individual course scoring
        for course in courses:
            # content_sim needs the database to query embeddings
            content_sim = self.content_scorer.score(db, student, course.id)
            skill_gap = self.skill_gap_scorer.score(db, student, course)
            rag_result = await self.rag_scorer.score(db, student, course, provider)
            pref_score = self.preference_scorer.score(db, student, course, preference)
            
            total_score = (
                (content_sim * 0.3) +
                (skill_gap * 0.3) +
                (rag_result.score * 0.2) +
                (pref_score * 0.2)
            )
            
            breakdown = ScoreBreakdown(
                skill_gap=skill_gap,
                content_sim=content_sim,
                preference=pref_score,
                rag_reasoning=rag_result.score,
                difficulty=course.difficulty,
                load=course.workload
            )
            
            results.append(RecommendationResult(
                course_id=course.id,
                subject_name=course.subject_name,
                score=total_score,
                breakdown=breakdown,
                reasoning=rag_result.reasoning,
                reason_tags=rag_result.tags
            ))
            
        results.sort(key=lambda x: x.score, reverse=True)
        
        # 2. Global Analysis (Skill Gap & Learning Path)
        # Requirement: Add analysis results and learning path
        analysis_data = None
        learning_path = []
        
        try:
            model = get_model(provider)
            deps = AnalysisDeps(student=student, courses=courses)
            
            if is_capable_model(model):
                analysis_res = await analysis_agent.run(
                    "Perform global analysis.",
                    model=model,
                    deps=deps
                )
                analysis_data = analysis_res.output.skill_gap_analysis
                learning_path = analysis_res.output.learning_path
            else:
                # Basic mock/heuristic fallback for weak models if needed, 
                # but for now we try to run it.
                analysis_res = await analysis_agent.run(
                    "Perform global analysis. Output valid JSON matching GlobalAnalysis schema.",
                    model=model,
                    deps=deps,
                    output_type=str
                )
                parsed = parse_global_analysis(analysis_res.output)
                analysis_data = parsed.skill_gap_analysis
                learning_path = parsed.learning_path
        except Exception as e:
            logger.error(f"Global analysis failed: {e}")

        return RecommendationResponse(
            results=results,
            skill_gap_analysis=analysis_data,
            learning_path=learning_path
        )
