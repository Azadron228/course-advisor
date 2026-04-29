from unittest.mock import patch

def test_create_course_admin(client, admin_token_headers):
    data = {
        "id": "CS101_NEW",
        "subject_name": "Intro to Plan Writing",
        "credits": 3.0,
        "description": "Learn to write implementation plans.",
        "skills_taught": ["Planning", "Design"],
        "difficulty": 0.5,
        "workload": 0.5
    }
    # We patch it where it is IMPORTED in the module we are testing
    with patch("app.api.v1.endpoints.admin.get_embedding") as mock_embedding:
        mock_embedding.return_value = [0.1] * 1536
        response = client.post("/api/v1/admin/courses", json=data, headers=admin_token_headers)
        assert response.status_code == 200
        assert response.json()["id"] == "CS101_NEW"
