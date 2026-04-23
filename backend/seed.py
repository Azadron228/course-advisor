import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.infrastructure.db.models import Base, CourseORM, UserORM
from app.infrastructure.ai.embeddings import get_embedding
from app.core.config import settings
from app.core.security import get_password_hash
import json

COURSES = [
    {
        "id": "CS401",
        "subject_name": "Artificial Intelligence",
        "credits": 6.0,
        "description": "Comprehensive introduction to AI, including machine learning, neural networks, and search algorithms.",
        "skills_taught": ["Python", "Machine Learning", "AI", "Algorithms"],
        "difficulty": 0.8,
        "workload": 0.7
    },
    {
        "id": "CS402",
        "subject_name": "Cloud Computing",
        "credits": 6.0,
        "description": "Deep dive into AWS, Azure, and Google Cloud. Focus on distributed systems and serverless architecture.",
        "skills_taught": ["AWS", "Docker", "Kubernetes", "Cloud Arch"],
        "difficulty": 0.6,
        "workload": 0.6
    },
    {
        "id": "CS403",
        "subject_name": "Cybersecurity Essentials",
        "credits": 6.0,
        "description": "Learn about network security, cryptography, and defensive programming techniques.",
        "skills_taught": ["Security", "Cryptography", "Linux", "Networking"],
        "difficulty": 0.7,
        "workload": 0.5
    },
    {
        "id": "CS404",
        "subject_name": "Advanced Web Development",
        "credits": 6.0,
        "description": "Master React, Next.js, and modern frontend performance optimization.",
        "skills_taught": ["React", "JavaScript", "TypeScript", "Web Performance"],
        "difficulty": 0.5,
        "workload": 0.8
    }
]

def seed():
    print("Starting database seeding...")
    engine = create_engine(settings.DATABASE_URL)
    Session = sessionmaker(bind=engine)
    session = Session()

    # Seed Courses
    for c in COURSES:
        print(f"Seeding course: {c['subject_name']}")
        emb = get_embedding(c["description"])
        
        # Check if course exists
        course = session.query(CourseORM).filter(CourseORM.id == c["id"]).first()
        if not course:
            course = CourseORM(
                id=c["id"],
                subject_name=c["subject_name"],
                credits=c["credits"],
                description=c["description"],
                skills_taught=c["skills_taught"],
                difficulty=c["difficulty"],
                workload=c["workload"],
                embedding=emb
            )
            session.add(course)
        else:
            course.subject_name = c["subject_name"]
            course.description = c["description"]
            course.skills_taught = c["skills_taught"]
            course.embedding = emb
    
    # Seed Admin User
    print("Seeding admin user...")
    admin_email = "admin@example.com"
    admin_user = session.query(UserORM).filter(UserORM.email == admin_email).first()
    if not admin_user:
        admin_user = UserORM(
            email=admin_email,
            hashed_password=get_password_hash("admin"),
            full_name="System Administrator",
            is_admin=True
        )
        session.add(admin_user)
    else:
        admin_user.is_admin = True
    
    session.commit()
    session.close()
    print("Seeding complete.")

if __name__ == "__main__":
    seed()
