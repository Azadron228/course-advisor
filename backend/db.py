import os
import psycopg
from pgvector.psycopg import register_vector

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://advisor:advisor_password@localhost:5432/course_advisor")

def get_connection():
    conn = psycopg.connect(DATABASE_URL)
    register_vector(conn)
    return conn

def init_db():
    conn = psycopg.connect(DATABASE_URL, autocommit=True)
    with conn.cursor() as cur:
        cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
        cur.execute("""
        CREATE TABLE IF NOT EXISTS courses (
            id VARCHAR PRIMARY KEY,
            subject_name VARCHAR NOT NULL,
            credits FLOAT NOT NULL,
            description TEXT NOT NULL,
            skills_taught JSONB NOT NULL,
            difficulty FLOAT CHECK (difficulty >= 0 AND difficulty <= 1),
            workload FLOAT CHECK (workload >= 0 AND workload <= 1),
            embedding VECTOR(1536)
        );
        """)
    conn.close()

if __name__ == '__main__':
    init_db()
    print("Database initialized successfully.")
