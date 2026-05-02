from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.infrastructure.db.models import CourseORM, CourseMaterialORM, UserORM, CourseMaterialChunkORM
from app.infrastructure.ai.embeddings import get_embedding, chunk_text
from app.core.config import settings
from app.core.security import get_password_hash

COURSES = [
    {
        "subject_name": "Artificial Intelligence",
        "description": "Comprehensive introduction to AI, including machine learning, neural networks, and search algorithms.",
        "skills_taught": ["Python", "Machine Learning", "AI", "Algorithms"],
        "materials_content": """
# Introduction to Artificial Intelligence
Welcome to CS401. This course covers:
- **Search Algorithms**: A*, BFS, DFS.
- **Machine Learning**: Linear Regression to Neural Nets.
- **Ethics**: The impact of AI on society.

## Recommended Reading
Check out the official documentation for [Scikit-Learn](https://scikit-learn.org).
        """
    },
    {
        "subject_name": "Cloud Computing",
        "description": "Deep dive into AWS, Azure, and Google Cloud. Focus on distributed systems and serverless architecture.",
        "skills_taught": ["AWS", "Docker", "Kubernetes", "Cloud Arch"],
        "materials_content": """
# Cloud Computing Architecture
Master the cloud with CS402:
- **Virtualization**: How VMs work.
- **Containers**: Docker and Kubernetes orchestration.
- **Serverless**: Lambda and Cloud Functions.
        """
    },
    {
        "subject_name": "Cybersecurity Essentials",
        "description": "Learn about network security, cryptography, and defensive programming techniques.",
        "skills_taught": ["Security", "Cryptography", "Linux", "Networking"],
        "materials_content": """
# Cybersecurity Fundamentals
Protecting systems in CS403:
- **Encryption**: RSA, AES, and public key infra.
- **Penetration Testing**: Ethical hacking basics.
- **Network Defense**: Firewalls and IDS.
        """
    },
    {
        "subject_name": "Advanced Web Development",
        "description": "Master React, Next.js, and modern frontend performance optimization.",
        "skills_taught": ["React", "JavaScript", "TypeScript", "Web Performance"],
        "materials_content": """
# Advanced Web Development
Building modern apps in CS404:
- **Frameworks**: React and Next.js (App Router).
- **Type Safety**: TypeScript at scale.
- **Optimization**: Core Web Vitals and SSR.
        """
    },
]


def seed():
    print("Starting database seeding...")
    engine = create_engine(settings.DATABASE_URL)
    Session = sessionmaker(bind=engine)
    session = Session()

    # Seed Courses
    for c in COURSES:
        print(f"Seeding course: {c['subject_name']}")
        
        # Check if course exists by subject_name
        course = session.query(CourseORM).filter(CourseORM.subject_name == c["subject_name"]).first()
        
        # NOW ONLY USES DESCRIPTION for course embedding
        emb = get_embedding(c["description"])

        if not course:
            course = CourseORM(
                subject_name=c["subject_name"],
                description=c["description"],
                skills_taught=c["skills_taught"],
                embedding=emb,
            )
            session.add(course)
            session.flush() # Get ID
            
            # Add material
            material = CourseMaterialORM(
                course_id=course.id,
                filename="syllabus.md",
                content=c["materials_content"],
                status="analyzed"
            )
            session.add(material)
            session.flush()

            # Chunk and Seed Material
            text_chunks = chunk_text(c["materials_content"])
            for i, chunk_txt in enumerate(text_chunks):
                chunk_emb = get_embedding(chunk_txt)
                chunk_orm = CourseMaterialChunkORM(
                    material_id=material.id,
                    content=chunk_txt,
                    embedding=chunk_emb,
                    chunk_index=i
                )
                session.add(chunk_orm)
        else:
            course.subject_name = c["subject_name"]
            course.description = c["description"]
            course.skills_taught = c["skills_taught"]
            course.embedding = emb
            
            # Update or Add material
            existing_material = session.query(CourseMaterialORM).filter(
                CourseMaterialORM.course_id == course.id,
                CourseMaterialORM.filename == "syllabus.md"
            ).first()
            if existing_material:
                existing_material.content = c["materials_content"]
                # Clear old chunks and re-chunk
                session.query(CourseMaterialChunkORM).filter(
                    CourseMaterialChunkORM.material_id == existing_material.id
                ).delete()
                
                text_chunks = chunk_text(c["materials_content"])
                for i, chunk_txt in enumerate(text_chunks):
                    chunk_emb = get_embedding(chunk_txt)
                    chunk_orm = CourseMaterialChunkORM(
                        material_id=existing_material.id,
                        content=chunk_txt,
                        embedding=chunk_emb,
                        chunk_index=i
                    )
                    session.add(chunk_orm)
            else:
                material = CourseMaterialORM(
                    course_id=course.id,
                    filename="syllabus.md",
                    content=c["materials_content"],
                    status="analyzed"
                )
                session.add(material)
                session.flush()

                # Chunk and Seed Material
                text_chunks = chunk_text(c["materials_content"])
                for i, chunk_txt in enumerate(text_chunks):
                    chunk_emb = get_embedding(chunk_txt)
                    chunk_orm = CourseMaterialChunkORM(
                        material_id=material.id,
                        content=chunk_txt,
                        embedding=chunk_emb,
                        chunk_index=i
                    )
                    session.add(chunk_orm)

    # Seed Admin User
    print("Seeding admin user...")
    admin_email = "admin@example.com"
    admin_user = session.query(UserORM).filter(UserORM.email == admin_email).first()
    if not admin_user:
        admin_user = UserORM(
            email=admin_email,
            hashed_password=get_password_hash("admin"),
            full_name="System Administrator",
            is_admin=True,
        )
        session.add(admin_user)
    else:
        admin_user.is_admin = True

    session.commit()
    session.close()
    print("Seeding complete.")


if __name__ == "__main__":
    seed()
