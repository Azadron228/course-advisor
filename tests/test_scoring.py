import unittest
from backend.scoring.skill_gap import SkillGapScorer
from backend.models import Student, Course

class TestSkillGapScorer(unittest.TestCase):
    def test_skill_gap_score(self):
        student = Student(id="S1", name="A", transcript=[], current_skills=["Python"])
        course = Course(
            id="C1", subject_name="Adv Python", credits=6, 
            description="...", prerequisites=[], 
            skills_taught=["Python", "Django", "FastAPI"],
            difficulty=0.5, workload=0.5
        )
        scorer = SkillGapScorer()
        score = scorer.score(student, course)
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
        score = scorer.score(student, course)
        self.assertEqual(score, 0.0)

if __name__ == '__main__':
    unittest.main()
