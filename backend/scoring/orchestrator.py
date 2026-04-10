from typing import List
from models import (
    Student, Course, UserPreference, 
    RecommendationResponse, RecommendationResult, ScoreBreakdown,
    ModelProvider
)
from scoring.content import ContentScorer
from scoring.skill_gap import SkillGapScorer
from scoring.rag import RAGScorer
from scoring.preference import PreferenceScorer

class HybridScorer:
    def __init__(self):
        self.content_scorer = ContentScorer()
        self.skill_gap_scorer = SkillGapScorer()
        self.rag_scorer = RAGScorer()
        self.preference_scorer = PreferenceScorer()
        
    async def recommend(
        self, 
        student: Student, 
        courses: List[Course], 
        preference: UserPreference,
        provider: ModelProvider = ModelProvider.AUTO
    ) -> RecommendationResponse:
        results = []
        
        for course in courses:
            # 1. Get individual component scores
            content_sim = self.content_scorer.score(student, course.id)
            skill_gap = self.skill_gap_scorer.score(student, course)
            rag_result = await self.rag_scorer.score(student, course, provider)
            pref_score = self.preference_scorer.score(student, course, preference)
            
            # 2. Apply weights (as per spec section 4)
            # Content: 30%, Skill Gap: 30%, RAG: 20%, Preference: 20%
            total_score = (
                (content_sim * 0.3) +
                (skill_gap * 0.3) +
                (rag_result.score * 0.2) +
                (pref_score * 0.2)
            )
            
            # 3. Build breakdown
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
            
        # 4. Sort by total score descending
        results.sort(key=lambda x: x.score, reverse=True)
        
        return RecommendationResponse(results=results)
