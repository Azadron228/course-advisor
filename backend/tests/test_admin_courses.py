from unittest.mock import patch

def test_create_course_admin(client, admin_token_headers):
    data = {
        "subject_name": "Intro to Plan Writing",
        "description": "Learn to write implementation plans.",
        "skills_taught": ["Planning", "Design"],
    }
    # We patch it where it is IMPORTED in the module we are testing
    with patch("app.api.v1.endpoints.admin.get_embedding") as mock_embedding:
        mock_embedding.return_value = [0.1] * 1536
        response = client.post("/api/v1/admin/courses", json=data, headers=admin_token_headers)
        assert response.status_code == 200
        assert isinstance(response.json()["id"], int)
        assert response.json()["subject_name"] == "Intro to Plan Writing"
        assert "materials" in response.json()
        assert response.json()["materials"] == []

def test_upload_material_admin(client, admin_token_headers):
    # First create a course
    data = {
        "subject_name": "Test Course for Materials",
        "description": "Description",
        "skills_taught": ["Skill"],
    }
    with patch("app.api.v1.endpoints.admin.get_embedding") as mock_embedding:
        mock_embedding.return_value = [0.1] * 1536
        create_res = client.post("/api/v1/admin/courses", json=data, headers=admin_token_headers)
        course_id = create_res.json()["id"]

        # Now upload a material
        files = {"file": ("test.txt", b"Hello material content", "text/plain")}
        upload_res = client.post(f"/api/v1/admin/courses/{course_id}/materials", files=files, headers=admin_token_headers)
        assert upload_res.status_code == 200
        assert upload_res.json()["filename"] == "test.txt"
        assert upload_res.json()["status"] == "pending"

        # Check course has materials now
        get_res = client.get("/api/v1/admin/courses", headers=admin_token_headers)
        course = next(c for c in get_res.json() if c["id"] == course_id)
        assert len(course["materials"]) == 1
        assert course["materials"][0]["filename"] == "test.txt"
