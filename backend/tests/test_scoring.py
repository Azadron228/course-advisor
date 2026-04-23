import unittest
from unittest.mock import MagicMock
from sqlalchemy.orm import Session
from backend.app.scoring.skill_gap import SkillGapScorer
from backend.app.schemas.course import Student, Course

class TestSkillGapScorer(unittest.TestCase):
    def setUp(self):
        self.mock_db = MagicMock(spec=Session)

    def test_skill_gap_score(self):
        student = Student(id="S1", name="A", transcript=[], current_skills=["Python"])
        course = Course(
            id="C1", subject_name="Adv Python", credits=6, 
            description="...", prerequisites=[], 
            skills_taught=["Python", "Django", "FastAPI"],
            difficulty=0.5, workload=0.5
        )
        scorer = SkillGapScorer()
        score = scorer.score(self.mock_db, student, course)
        # 2 out of 3 skills are new (Django, FastAPI). 
        # Score is ratio of new skills: 2/3 = 0.666...
        self.assertAlmostEqual(score, 2/3, places=2)

    def test_perfect_match(self):
        student = Student(id="S1", name="A", transcript=[], current_skills=["Python", "Django"])
        course = Course(
            id="C1", subject_name="...", credits=6, 
            description="...", prerequisites=[], 
            skills_taught=["Python", "Django"],
            difficulty=0.5, workload=0.5
        )
        scorer = SkillGapScorer()
        score = scorer.score(self.mock_db, student, course)
        self.assertEqual(score, 0.0)

from backend.app.scoring.content import ContentScorer
from backend.app.schemas.course import TranscriptEntry

class TestContentScorer(unittest.TestCase):
    def setUp(self):
        self.mock_db = MagicMock(spec=Session)

    def test_content_score(self):
        student = Student(
            id="S1", name="A", 
            transcript=[TranscriptEntry(subject_name="AI", credits=6, mark=80)], 
            current_skills=[]
        )
        
        # Mock db.scalar to return a course and then a score
        mock_course = MagicMock()
        mock_course.embedding = [0.1] * 1536
        self.mock_db.scalar.side_effect = [mock_course, 0.85]
        
        # Mock get_embedding
        with unittest.mock.patch('backend.app.scoring.content.get_embedding', return_value=[0.1]*1536):
            scorer = ContentScorer()
            score = scorer.score(self.mock_db, student, "C1")
            self.assertEqual(score, 0.85)

from backend.app.scoring.preference import PreferenceScorer
from backend.app.schemas.course import UserPreference

class TestPreferenceScorer(unittest.TestCase):
    def setUp(self):
        self.mock_db = MagicMock(spec=Session)

    def test_preference_score(self):
        student = Student(id="S1", name="A", transcript=[], current_skills=[])
        course = Course(
            id="C1", subject_name="Intro to AI", credits=6, 
            description="Deep learning and neural networks", 
            prerequisites=[], 
            skills_taught=[],
            difficulty=0.4, workload=0.4
        )
        preference = UserPreference(
            interest_tags=["AI", "Neural"],
            target_difficulty=0.5,
            max_workload=0.5
        )
        scorer = PreferenceScorer()
        score = scorer.score(self.mock_db, student, course, preference)
        # AI matches subject_name, Neural matches description. 2/2 = 1.0. 
        # Difficulty and workload are within limits. Penalty = 1.0.
        self.assertEqual(score, 1.0)

    def test_penalty_score(self):
        student = Student(id="S1", name="A", transcript=[], current_skills=[])
        course = Course(
            id="C1", subject_name="Intro to AI", credits=6, 
            description="...", prerequisites=[], 
            skills_taught=[],
            difficulty=0.8, workload=0.8
        )
        preference = UserPreference(
            interest_tags=["AI"],
            target_difficulty=0.5,
            max_workload=0.5
        )
        scorer = PreferenceScorer()
        score = scorer.score(self.mock_db, student, course, preference)
        # Interest match: 1.0
        # Difficulty penalty: 1 - (0.8 - 0.5) = 0.7
        # Workload penalty: 1 - (0.8 - 0.5) = 0.7
        # Total score: 1.0 * 0.7 * 0.7 = 0.49
        self.assertAlmostEqual(score, 0.49, places=2)

if __name__ == '__main__':
    unittest.main()
