import unittest
from backend.app.models import TranscriptEntry, Student, Course, ModelProvider
from pydantic import ValidationError

class TestModels(unittest.TestCase):
    def test_model_provider_enum(self):
        self.assertEqual(ModelProvider.OPENAI, "openai")
        self.assertEqual(ModelProvider.OLLAMA, "ollama")
        self.assertEqual(ModelProvider.GEMINI, "gemini")
        self.assertEqual(ModelProvider.AUTO, "auto")

    def test_transcript_entry_validation(self):
        entry = TranscriptEntry(subject_name="Math", credits=6.0, mark=85.0)
        self.assertEqual(entry.subject_name, "Math")
        self.assertEqual(entry.mark, 85.0)
        
        with self.assertRaises(ValidationError):
            TranscriptEntry(subject_name="Invalid", credits=6.0, mark=105.0)

    def test_student_model(self):
        entry = TranscriptEntry(subject_name="Algorithms", credits=6.0, mark=90.0)
        student = Student(
            id="S123",
            name="Alice",
            transcript=[entry],
            current_skills=["Python", "SQL"]
        )
        self.assertEqual(student.name, "Alice")
        self.assertEqual(len(student.transcript), 1)

    def test_course_model(self):
        course = Course(
            id="CS101",
            subject_name="Intro to CS",
            credits=6.0,
            description="Basics of programming",
            prerequisites=[],
            skills_taught=["Programming"],
            difficulty=0.2,
            workload=0.3
        )
        self.assertEqual(course.id, "CS101")
        
        with self.assertRaises(ValidationError):
             Course(
                id="CS102",
                subject_name="Advanced CS",
                credits=6.0,
                description="Complex stuff",
                prerequisites=[],
                skills_taught=["Algorithms"],
                difficulty=1.5, # Invalid
                workload=0.5
            )

if __name__ == '__main__':
    unittest.main()
