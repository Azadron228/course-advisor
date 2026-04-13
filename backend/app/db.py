import os
import sqlite3
import psycopg2
from pgvector.psycopg2 import register_vector
from typing import Optional, List
from .models import Course, UserInDB

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://advisor:advisor_password@localhost:5432/course_advisor")
USERS_DB = "users.db"

def get_connection():
    conn = psycopg2.connect(DATABASE_URL)
    register_vector(conn)
    return conn

def init_users_db():
    conn = sqlite3.connect(USERS_DB)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            email TEXT,
            full_name TEXT,
            hashed_password TEXT,
            disabled BOOLEAN DEFAULT 0
        )
    """)
    conn.commit()
    conn.close()

def get_user_by_username(username: str) -> Optional[UserInDB]:
    conn = sqlite3.connect(USERS_DB)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE username = ?", (username,))
    row = cur.fetchone()
    conn.close()
    if row:
        return UserInDB(
            username=row["username"],
            email=row["email"],
            full_name=row["full_name"],
            hashed_password=row["hashed_password"],
            disabled=bool(row["disabled"])
        )
    return None

def create_user(username: str, hashed_password: str, email: str = None, full_name: str = None):
    conn = sqlite3.connect(USERS_DB)
    cur = conn.cursor()
    try:
        cur.execute(
            "INSERT INTO users (username, hashed_password, email, full_name) VALUES (?, ?, ?, ?)",
            (username, hashed_password, email, full_name)
        )
        conn.commit()
    finally:
        conn.close()

# Initialize users DB on import
init_users_db()

def get_all_courses():
    courses = []
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id, subject_name, credits, description, skills_taught, difficulty, workload FROM courses")
            for row in cur.fetchall():
                import json
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
                    prerequisites=[]
                ))
    return courses
