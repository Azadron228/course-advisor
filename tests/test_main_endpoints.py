import os
os.environ["TESTING"] = "1"

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.app.main import app
from backend.app.db import get_db, Base
from backend.app.models import UserORM

# Setup test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

def test_register_user():
    response = client.post(
        "/register",
        json={"email": "test@example.com", "password": "password123", "full_name": "Test User"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@example.com"
    assert data["full_name"] == "Test User"
    assert "password" not in data

def test_register_duplicate_user():
    client.post(
        "/register",
        json={"email": "test@example.com", "password": "password123", "full_name": "Test User"},
    )
    response = client.post(
        "/register",
        json={"email": "test@example.com", "password": "password123", "full_name": "Test User"},
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Email already registered"

def test_login_for_access_token():
    client.post(
        "/register",
        json={"email": "test@example.com", "password": "password123", "full_name": "Test User"},
    )
    response = client.post(
        "/token",
        data={"username": "test@example.com", "password": "password123"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_invalid_credentials():
    client.post(
        "/register",
        json={"email": "test@example.com", "password": "password123", "full_name": "Test User"},
    )
    response = client.post(
        "/token",
        data={"username": "test@example.com", "password": "wrongpassword"},
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect email or password"

def test_get_recommendations_unauthorized():
    response = client.post(
        "/recommend",
        json={
            "student": {
                "id": "s1", "name": "S1", "transcript": [], "current_skills": []
            },
            "preference": {
                "interest_tags": [], "target_difficulty": 0.5, "max_workload": 0.5
            }
        },
    )
    assert response.status_code == 401

def test_get_recommendations_authorized():
    # Register and login
    client.post(
        "/register",
        json={"email": "test@example.com", "password": "password123", "full_name": "Test User"},
    )
    login_response = client.post(
        "/token",
        data={"username": "test@example.com", "password": "password123"},
    )
    token = login_response.json()["access_token"]

    # Mock scorer to avoid external dependencies
    from unittest.mock import patch
    with patch("backend.app.main.scorer.recommend") as mock_recommend:
        mock_recommend.return_value = {"results": []}
        
        response = client.post(
            "/recommend",
            json={
                "student": {
                    "id": "s1", "name": "S1", "transcript": [], "current_skills": []
                },
                "preference": {
                    "interest_tags": [], "target_difficulty": 0.5, "max_workload": 0.5
                }
            },
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        assert "results" in response.json()
