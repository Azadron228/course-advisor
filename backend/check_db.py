import sys
from app.infrastructure.db.session import SessionLocal
from app.infrastructure.db.models import CourseMaterialORM, LessonORM

with SessionLocal() as db:
    materials = db.query(CourseMaterialORM).all()
    print(f"Total materials: {len(materials)}")
    for m in materials:
        print(f"Material {m.id} content length: {len(m.content) if m.content else 0}")
    
    lessons = db.query(LessonORM).all()
    print(f"Total lessons: {len(lessons)}")
    for l in lessons:
        print(f"Lesson {l.id} content length: {len(l.content) if l.content else 0}")
