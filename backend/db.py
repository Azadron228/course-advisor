import os
import psycopg
from pgvector.psycopg import register_vector

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://advisor:advisor_password@localhost:5432/course_advisor")

def get_connection():
    conn = psycopg.connect(DATABASE_URL)
    register_vector(conn)
    return conn

if __name__ == '__main__':
    with get_connection() as conn:
        print("Connected to database successfully.")
