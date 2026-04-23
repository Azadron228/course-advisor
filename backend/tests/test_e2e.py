import unittest
import asyncio
from backend.app.parser import parse_transcript_html
from backend.app.scoring.orchestrator import HybridScorer
from backend.app.schemas.course import Student, UserPreference, Course
from backend.app.schemas.course import TranscriptEntry # In case it's needed
import os

class TestEndToEnd(unittest.TestCase):
    def setUp(self):
        self.scorer = HybridScorer()
        with open('transcipt.html', 'r') as f:
            self.html = f.read()

    def test_full_pipeline_logic(self):
        # 1. Test Parser
        entries = parse_transcript_html(self.html)
        self.assertGreater(len(entries), 0)
        
        # 2. Mock Student and Preference
        student = Student(
            id="test_student",
            name="Test User",
            transcript=entries,
            current_skills=["Python"]
        )
        pref = UserPreference(
            interest_tags=["AI", "Security"],
            target_difficulty=0.5,
            max_workload=0.5
        )
        
        # 3. Mock some courses
        courses = [
            Course(id="C1", subject_name="AI intro", credits=6, description="AI", skills_taught=["AI"], difficulty=0.5, workload=0.5, prerequisites=[]),
            Course(id="C2", subject_name="Web", credits=6, description="Web", skills_taught=["Web"], difficulty=0.5, workload=0.5, prerequisites=[])
        ]
        
        # 4. Test Orchestrator
        from unittest.mock import AsyncMock, MagicMock
        from backend.app.agent import AgentRecommendation
        
        # Mock RAGScorer to avoid agent complexity in this test
        self.scorer.rag_scorer.score = AsyncMock(return_value=AgentRecommendation(
            score=0.9, reasoning="Excellent fit for the student's profile.", tags=["AI"]
        ))
        
        db = MagicMock()
        resp = asyncio.run(self.scorer.recommend(db, student, courses, pref))
        
        self.assertEqual(len(resp.results), 2)
        self.assertGreater(resp.results[0].score, 0)

if __name__ == '__main__':
    unittest.main()
