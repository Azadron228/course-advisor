import unittest
import os
import yaml

class TestScaffolding(unittest.TestCase):
    def test_docker_compose_exists(self):
        self.assertTrue(os.path.exists('docker-compose.yml'), "docker-compose.yml is missing")

    def test_backend_requirements_exists(self):
        self.assertTrue(os.path.exists('backend/requirements.txt'), "backend/requirements.txt is missing")

    def test_frontend_requirements_exists(self):
        self.assertTrue(os.path.exists('frontend/requirements.txt'), "frontend/requirements.txt is missing")

    def test_frontend_requirements_content(self):
        requirements_path = 'frontend/requirements.txt'
        if not os.path.exists(requirements_path):
             self.skipTest("frontend/requirements.txt is missing")
        with open(requirements_path, 'r') as f:
            content = f.read()
        self.assertIn('streamlit', content)
        self.assertIn('httpx', content)
        self.assertIn('pandas', content)

    def test_docker_compose_services(self):
        with open('docker-compose.yml', 'r') as f:
            config = yaml.safe_load(f)
        
        services = config.get('services', {})
        self.assertIn('db', services)
        self.assertIn('backend', services)
        self.assertIn('frontend', services)

        # Check db service
        db = services['db']
        self.assertIn(db.get('image'), ['postgres:16', 'pgvector/pgvector:pg16', 'ankane/pgvector:v0.7.0'])
        
        # Check ports
        self.assertIn('5432:5432', db.get('ports', []))
        self.assertIn('8000:8000', services['backend'].get('ports', []))
        self.assertIn('8501:8501', services['frontend'].get('ports', []))

        # Check environment variables for DB
        db_env = db.get('environment', {})
        if isinstance(db_env, list):
             db_env = {item.split('=')[0]: item.split('=')[1] for item in db_env}
        self.assertIn('POSTGRES_DB', db_env)
        self.assertIn('POSTGRES_USER', db_env)
        self.assertIn('POSTGRES_PASSWORD', db_env)

if __name__ == '__main__':
    unittest.main()
