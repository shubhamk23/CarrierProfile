"""Tests for the /api/profile router (app/routers/profile.py).

All tests mock the filesystem open() call so they never depend on the real
profile.json file being present or having a specific shape.
"""
from unittest.mock import patch
from fastapi.testclient import TestClient


class TestGetProfile:
    def test_returns_200(self, client):
        response = client.get("/api/profile")
        assert response.status_code == 200

    def test_response_contains_name(self, client):
        body = client.get("/api/profile").json()
        assert "name" in body

    def test_response_contains_skills(self, client):
        body = client.get("/api/profile").json()
        assert "skills" in body

    def test_response_contains_experience_list(self, client):
        body = client.get("/api/profile").json()
        assert isinstance(body.get("experience"), list)

    def test_file_not_found_returns_500(self):
        from app.main import app

        with patch("builtins.open", side_effect=FileNotFoundError("no file")):
            with TestClient(app, raise_server_exceptions=False) as c:
                response = c.get("/api/profile")
        assert response.status_code == 500


class TestGetExperience:
    def test_returns_200(self, client):
        response = client.get("/api/experience")
        assert response.status_code == 200

    def test_returns_list(self, client):
        body = client.get("/api/experience").json()
        assert isinstance(body, list)

    def test_each_item_has_required_fields(self, client):
        items = client.get("/api/experience").json()
        required = {"company", "role", "location", "period", "description", "technologies"}
        for item in items:
            missing = required - item.keys()
            assert not missing, f"Experience item missing: {missing}"

    def test_file_not_found_returns_500(self):
        from app.main import app

        with patch("builtins.open", side_effect=FileNotFoundError):
            with TestClient(app, raise_server_exceptions=False) as c:
                response = c.get("/api/experience")
        assert response.status_code == 500


class TestGetSkills:
    def test_returns_200(self, client):
        response = client.get("/api/skills")
        assert response.status_code == 200

    def test_returns_skills_object_with_categories(self, client):
        body = client.get("/api/skills").json()
        expected_categories = {
            "languages",
            "ml_dl_frameworks",
            "computer_vision",
            "generative_ai_nlp",
            "mlops_devops",
            "cloud_data",
            "software_engineering",
        }
        missing = expected_categories - body.keys()
        assert not missing, f"Skills missing categories: {missing}"


class TestGetProjects:
    def test_returns_200(self, client):
        response = client.get("/api/projects")
        assert response.status_code == 200

    def test_returns_list(self, client):
        body = client.get("/api/projects").json()
        assert isinstance(body, list)

    def test_each_project_has_title(self, client):
        projects = client.get("/api/projects").json()
        for project in projects:
            assert "title" in project


class TestGetEducation:
    def test_returns_200(self, client):
        response = client.get("/api/education")
        assert response.status_code == 200

    def test_returns_object_with_degree(self, client):
        body = client.get("/api/education").json()
        assert "degree" in body

    def test_returns_object_with_institution(self, client):
        body = client.get("/api/education").json()
        assert "institution" in body


class TestGetCertifications:
    def test_returns_200(self, client):
        response = client.get("/api/certifications")
        assert response.status_code == 200

    def test_returns_list(self, client):
        body = client.get("/api/certifications").json()
        assert isinstance(body, list)

    def test_each_certification_has_title_and_issuer(self, client):
        certs = client.get("/api/certifications").json()
        for cert in certs:
            assert "title" in cert
            assert "issuer" in cert


class TestGetAchievements:
    def test_returns_200(self, client):
        response = client.get("/api/achievements")
        assert response.status_code == 200

    def test_returns_list(self, client):
        body = client.get("/api/achievements").json()
        assert isinstance(body, list)

    def test_each_award_has_required_fields(self, client):
        awards = client.get("/api/achievements").json()
        for award in awards:
            assert "title" in award
            assert "year" in award
            assert "description" in award
