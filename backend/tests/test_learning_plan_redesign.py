import pytest
from fastapi.testclient import TestClient
from app.main import app

def test_plan_summary_list(client: TestClient, admin_token_headers):
    # Generate a plan first to ensure we have data
    client.post("/api/v1/learning-plan/generate", 
        json={
            "goal": "Test Goal",
            "skill_level": "Beginner",
            "learning_style": "Practical",
            "study_time": 10,
            "interests": ["coding"]
        },
        headers=admin_token_headers
    )
    
    r = client.get("/api/v1/learning-plan/", headers=admin_token_headers)
    assert r.status_code == 200
    plans = r.json()
    assert isinstance(plans, list)
    if plans:
        assert "step_count" in plans[0]
        assert "steps" not in plans[0]
        assert "last_interacted_at" in plans[0]

def test_plan_detail_no_materials(client: TestClient, admin_token_headers):
    r_list = client.get("/api/v1/learning-plan/", headers=admin_token_headers)
    plans = r_list.json()
    if not plans: return

    plan_id = plans[0]["id"]
    r = client.get(f"/api/v1/learning-plan/{plan_id}", headers=admin_token_headers)
    assert r.status_code == 200
    plan = r.json()
    assert "steps" in plan
    if plan["steps"]:
        assert "materials" not in plan["steps"][0]

def test_step_detail_with_materials(client: TestClient, admin_token_headers):
    r_list = client.get("/api/v1/learning-plan/", headers=admin_token_headers)
    plans = r_list.json()
    if not plans: return

    plan_id = plans[0]["id"]
    r_plan = client.get(f"/api/v1/learning-plan/{plan_id}", headers=admin_token_headers)
    plan = r_plan.json()
    if not plan["steps"]: return

    step_order = plan["steps"][0]["order"]
    r = client.get(f"/api/v1/learning-plan/{plan_id}/steps/{step_order}", headers=admin_token_headers)
    assert r.status_code == 200
    lesson = r.json()
    assert "materials" in lesson
    assert "content" in lesson
