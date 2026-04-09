import os
import psycopg
from pgvector.psycopg import register_vector

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://advisor:advisor_password@localhost:5432/course_advisor")

from backend.models import Course
import json

def get_connection():
    conn = psycopg.connect(DATABASE_URL)
    register_vector(conn)
    return conn

def get_all_courses():
    courses = []
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id, subject_name, credits, description, skills_taught, difficulty, workload FROM courses")
            for row in cur.fetchall():
                # skills_taught is JSONB in DB
                skills = row[4]
                if isinstance(skills, str):
                    skills = json.loads(skills)
                
                courses.append(Course(
                    id=row[0],
                    subject_name=row[1],
                    credits=row[2],
                    description=row[3],
                    skills_taught=skills,
                    difficulty=row[5],
                    workload=row[6],
                    prerequisites=[] # Default for now
                ))
    return courses

if __name__ == '__main__':
    with get_connection() as conn:
        print("Connected to database successfully.")
