from app.infrastructure.db.session import SessionLocal
from app.infrastructure.db.models import LessonORM

with SessionLocal() as db:
    lessons = db.query(LessonORM).all()
    print(f"Total lessons: {len(lessons)}")
    for lesson in lessons:
        print(f"Lesson {lesson.id} content length: {len(lesson.content) if lesson.content else 0}")
