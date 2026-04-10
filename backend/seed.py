from db import get_connection
from embeddings import get_embedding
import json
import os

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
    with get_connection() as conn:
        with conn.cursor() as cur:
            from pgvector.psycopg2 import register_vector
            register_vector(cur)
            
            for c in COURSES:
                print(f"Seeding course: {c['subject_name']}")
                emb = get_embedding(c["description"])
                cur.execute(
                    """
                    INSERT INTO courses (id, subject_name, credits, description, skills_taught, difficulty, workload, embedding) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s) 
                    ON CONFLICT (id) DO UPDATE SET 
                        subject_name = EXCLUDED.subject_name,
                        description = EXCLUDED.description,
                        skills_taught = EXCLUDED.skills_taught,
                        embedding = EXCLUDED.embedding
                    """,
                    (c["id"], c["subject_name"], c["credits"], c["description"], json.dumps(c["skills_taught"]), c["difficulty"], c["workload"], emb)
                )
    print("Seeding complete.")

if __name__ == "__main__":
    seed()
