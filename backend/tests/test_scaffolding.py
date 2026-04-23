import unittest
import os
import yaml

class TestScaffolding(unittest.TestCase):
    def test_docker_compose_exists(self):
        self.assertTrue(os.path.exists('docker-compose.yml'), "docker-compose.yml is missing")

    def test_backend_requirements_exists(self):
        self.assertTrue(os.path.exists('backend/requirements.txt'), "backend/requirements.txt is missing")

    def test_frontend_package_json_exists(self):
        self.assertTrue(os.path.exists('frontend/package.json'), "frontend/package.json is missing")

    def test_frontend_package_json_content(self):
        package_json_path = 'frontend/package.json'
        if not os.path.exists(package_json_path):
             self.skipTest("frontend/package.json is missing")
        with open(package_json_path, 'r') as f:
            content = f.read()
        self.assertIn('next', content)
        self.assertIn('react', content)

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
        self.assertIn('8000:8000', services['backend'].get('ports', []))
        self.assertIn('3000:3000', services['frontend'].get('ports', []))

        # Check environment variables for DB
        db_env = db.get('environment', {})
        if isinstance(db_env, list):
             db_env = {item.split('=')[0]: item.split('=')[1] for item in db_env}
        self.assertIn('POSTGRES_DB', db_env)
        self.assertIn('POSTGRES_USER', db_env)
        self.assertIn('POSTGRES_PASSWORD', db_env)

if __name__ == '__main__':
    unittest.main()
