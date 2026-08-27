"""
Unit tests for API Keys, Telemetry & Evaluation RBAC Governance
"""

import pytest
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from src.apps.projects.models import Project


@pytest.fixture
def regular_user(db):
    return User.objects.create_user(username="regular_user_gov", password="password123")


@pytest.fixture
def staff_admin(db):
    return User.objects.create_user(username="staff_admin_gov", password="password123", is_staff=True)


@pytest.fixture
def test_project(db, staff_admin):
    return Project.objects.create(
        project_id="gov_proj_1",
        display_name="Governance Project",
        storage_type="postgres",
        user=staff_admin,
    )


@pytest.mark.django_db
class TestAdminGovernanceRBAC:
    def test_non_admin_cannot_access_api_keys(self, regular_user, test_project):
        client = APIClient()
        client.force_authenticate(user=regular_user)

        # GET /api/keys/
        get_res = client.get("/rag/api/keys/")
        assert get_res.status_code == 403

        # POST /api/keys/
        post_res = client.post(
            "/rag/api/keys/",
            {
                "name": "Unauthorized Key",
                "project": test_project.id,
            },
            format="json",
        )
        assert post_res.status_code == 403

    def test_staff_admin_can_manage_api_keys(self, staff_admin, test_project):
        client = APIClient()
        client.force_authenticate(user=staff_admin)

        post_res = client.post(
            "/rag/api/keys/",
            {
                "name": "Admin Managed Key",
                "project": test_project.id,
            },
            format="json",
        )
        assert post_res.status_code == 201
        assert "key" in post_res.data

        get_res = client.get("/rag/api/keys/")
        assert get_res.status_code == 200

    def test_non_admin_cannot_access_usage_telemetry(self, regular_user):
        client = APIClient()
        client.force_authenticate(user=regular_user)

        res = client.get("/rag/api/usage/")
        assert res.status_code == 403

    def test_staff_admin_can_access_usage_telemetry(self, staff_admin):
        client = APIClient()
        client.force_authenticate(user=staff_admin)

        res = client.get("/rag/api/usage/")
        assert res.status_code == 200

    def test_non_admin_cannot_access_evaluation_endpoints(self, regular_user, test_project):
        client = APIClient()
        client.force_authenticate(user=regular_user)

        # Datasets
        assert client.get("/rag/api/datasets/").status_code == 403
        assert client.post("/rag/api/datasets/", {"name": "Test", "project": test_project.id}).status_code == 403

        # Runs
        assert client.get("/rag/api/runs/").status_code == 403
        assert client.post("/rag/api/runs/", {"project": test_project.id}).status_code == 403

        # Results
        assert client.get("/rag/api/results/").status_code == 403

    def test_staff_admin_can_access_evaluation_endpoints(self, staff_admin):
        client = APIClient()
        client.force_authenticate(user=staff_admin)

        assert client.get("/rag/api/datasets/").status_code == 200
        assert client.get("/rag/api/runs/").status_code == 200
        assert client.get("/rag/api/results/").status_code == 200
