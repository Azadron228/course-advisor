import unittest
import os
import time

class TestDatabaseSchema(unittest.TestCase):
    def setUp(self):
        self.db_url = os.getenv("DATABASE_URL", "postgresql://advisor:advisor_password@localhost:5432/course_advisor")
        # Give DB a second to be ready
        time.sleep(1)

    def test_schema_initialization(self):
        from backend.db import init_db, get_connection
        
        # Ensure we can connect and initialize without errors
        init_db()
        
        # Verify the table was created and the vector extension is loaded
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'courses';")
                columns = {row[0]: row[1] for row in cur.fetchall()}
                
                # Check for expected columns
                self.assertIn('id', columns)
                self.assertIn('subject_name', columns)
                self.assertIn('embedding', columns)
                self.assertEqual(columns['embedding'], 'USER-DEFINED')

if __name__ == '__main__':
    unittest.main()
