from app.infrastructure.db.session import SessionLocal
from app.infrastructure.db.models import CourseMaterialORM, LessonORM

with SessionLocal() as db:
    materials = db.query(CourseMaterialORM).all()
    print(f"Total materials: {len(materials)}")
    for material in materials:
        print(f"Material {material.id} content length: {len(material.content) if material.content else 0}")
    
    lessons = db.query(LessonORM).all()
    print(f"Total lessons: {len(lessons)}")
    for lesson in lessons:
        print(f"Lesson {lesson.id} content length: {len(lesson.content) if lesson.content else 0}")
