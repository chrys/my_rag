"""
Unit tests for Project Governance RBAC
"""

import pytest
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from src.apps.projects.models import Project


@pytest.fixture
def regular_user(db):
    return User.objects.create_user(username="test_regular", password="password123")


@pytest.fixture
def other_user(db):
    return User.objects.create_user(username="test_other", password="password123")


@pytest.fixture
def staff_admin(db):
    return User.objects.create_user(username="test_admin", password="password123", is_staff=True)


@pytest.fixture
def regular_project(db, regular_user):
    return Project.objects.create(
        project_id="proj_regular_1",
        display_name="Regular Project",
        storage_type="postgres",
        user=regular_user,
    )


@pytest.mark.django_db
class TestProjectGovernanceRBAC:
    def test_non_admin_cannot_create_project(self, regular_user):
        client = APIClient()
        client.force_authenticate(user=regular_user)

        response = client.post(
            "/api/projects/",
            {
                "project_id": "proj_new_fail",
                "display_name": "New Project Attempt",
                "storage_type": "postgres",
            },
            format="json",
        )
        assert response.status_code == 403
        assert "error" in response.data or "detail" in response.data

    def test_non_admin_cannot_update_project(self, regular_user, regular_project):
        client = APIClient()
        client.force_authenticate(user=regular_user)

        response = client.put(
            f"/api/projects/{regular_project.project_id}/",
            {
                "display_name": "Updated Display Name",
            },
            format="json",
        )
        assert response.status_code == 403

    def test_non_admin_cannot_delete_project(self, regular_user, regular_project):
        client = APIClient()
        client.force_authenticate(user=regular_user)

        response = client.delete(f"/api/projects/{regular_project.project_id}/")
        assert response.status_code == 403

    def test_staff_admin_can_create_project(self, staff_admin):
        client = APIClient()
        client.force_authenticate(user=staff_admin)

        response = client.post(
            "/api/projects/",
            {
                "project_id": "proj_admin_success",
                "display_name": "Admin Created Project",
                "storage_type": "postgres",
            },
            format="json",
        )
        assert response.status_code == 201
        assert response.data["project_id"] == "proj_admin_success"

    def test_staff_admin_can_update_and_delete_project(self, staff_admin, regular_project):
        client = APIClient()
        client.force_authenticate(user=staff_admin)

        # Update
        response = client.patch(
            f"/api/projects/{regular_project.project_id}/",
            {"display_name": "Admin Renamed Project"},
            format="json",
        )
        assert response.status_code == 200

        # Delete
        response = client.delete(f"/api/projects/{regular_project.project_id}/")
        assert response.status_code in [200, 204]

    def test_regular_user_can_read_and_set_prompt_on_own_project(self, regular_user, regular_project):
        client = APIClient()
        client.force_authenticate(user=regular_user)

        # Read project details
        get_res = client.get(f"/api/projects/{regular_project.project_id}/")
        assert get_res.status_code == 200

        # Set prompt
        post_prompt = client.post(
            f"/api/projects/{regular_project.project_id}/prompt/",
            {"content": "You are a helpful assistant."},
            format="json",
        )
        assert post_prompt.status_code == 200

        # Get prompt
        get_prompt = client.get(f"/api/projects/{regular_project.project_id}/prompt/")
        assert get_prompt.status_code == 200
        assert get_prompt.data["prompt"] == "You are a helpful assistant."
