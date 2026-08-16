import pytest
import os
import sys
import json
from django.test import RequestFactory, Client
from django.contrib.auth.models import User
from django.utils import timezone

# Add src to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../src')))

from src.apps.projects.models import Project
from src.apps.api.models import APIKey
from src.apps.chat.models import ChatFeedback
from src.apps.chat.views import chatbot_feedback
from src.apps.projects.views import project_feedback


@pytest.mark.django_db
class TestChatFeedbackModel:
    """Tests for ChatFeedback model"""

    def test_create_chat_feedback(self):
        user = User.objects.create_user(username="fbuser", password="password")
        project = Project.objects.create(
            project_id="postgres_feedback_model_test",
            display_name="Feedback Test Project",
            storage_type="postgres",
            user=user
        )

        fb = ChatFeedback.objects.create(
            project=project,
            message_id="msg_12345",
            conversation_id="conv_67890",
            customer_id="cust_99",
            value="up"
        )

        assert fb.project == project
        assert fb.value == "up"
        assert fb.message_id == "msg_12345"
        assert "Feedback Test Project - up" in str(fb)


@pytest.mark.django_db
class TestChatbotFeedbackAPI:
    """Tests for /api/chatbot/feedback/ endpoint"""

    def test_feedback_with_api_key_auth(self):
        user = User.objects.create_user(username="apiuser", password="password")
        project = Project.objects.create(
            project_id="postgres_api_feedback_test",
            display_name="API Feedback Project",
            storage_type="postgres",
            user=user
        )
        api_key = APIKey.objects.create(user=user, project=project, name="Key 1")

        client = Client()
        payload = {
            "message_id": "4b321a56-7890-4c12-b5e3-1a2b3c4d5e6f",
            "conversation_id": "9876fecd-1234-5678-9abc-def012345678",
            "customer_id": "42",
            "value": "up",
            "timestamp": "2026-08-16T10:30:00+00:00"
        }

        response = client.post(
            "/rag/api/chatbot/feedback/",
            data=json.dumps(payload),
            content_type="application/json",
            HTTP_X_API_KEY=api_key.key
        )

        assert response.status_code == 201
        data = response.json()
        assert data["status"] == "success"
        assert data["value"] == "up"
        assert data["project_id"] == project.project_id

        # Verify record in database
        fb = ChatFeedback.objects.get(id=data["feedback_id"])
        assert fb.project == project
        assert fb.message_id == "4b321a56-7890-4c12-b5e3-1a2b3c4d5e6f"
        assert fb.conversation_id == "9876fecd-1234-5678-9abc-def012345678"
        assert fb.customer_id == "42"
        assert fb.value == "up"

    def test_feedback_with_direct_api_url_and_store_id(self):
        user = User.objects.create_user(username="directuser", password="password")
        project = Project.objects.create(
            project_id="postgres_direct_url_test",
            display_name="Direct URL Project",
            storage_type="postgres",
            user=user
        )

        client = Client()
        payload = {
            "store_id": "postgres_direct_url_test",
            "message_id": "msg_direct_001",
            "value": "down",
            "customer_id": "100"
        }

        response = client.post(
            "/api/chatbot/feedback/",
            data=json.dumps(payload),
            content_type="application/json"
        )

        assert response.status_code == 201
        data = response.json()
        assert data["status"] == "success"
        assert data["value"] == "down"

        fb = ChatFeedback.objects.get(message_id="msg_direct_001")
        assert fb.value == "down"
        assert fb.project == project

    def test_feedback_validation_errors(self):
        client = Client()

        # Missing message_id
        res1 = client.post(
            "/rag/api/chatbot/feedback/",
            data=json.dumps({"store_id": "any", "value": "up"}),
            content_type="application/json"
        )
        assert res1.status_code == 400
        assert "message_id" in res1.json()["error"]

        # Invalid value (not 'up' or 'down')
        res2 = client.post(
            "/rag/api/chatbot/feedback/",
            data=json.dumps({"message_id": "123", "value": "great"}),
            content_type="application/json"
        )
        assert res2.status_code == 400
        assert "Invalid feedback value" in res2.json()["error"]

        # Unknown project
        res3 = client.post(
            "/rag/api/chatbot/feedback/",
            data=json.dumps({"message_id": "123", "value": "up", "store_id": "nonexistent_proj"}),
            content_type="application/json"
        )
        assert res3.status_code == 404

    def test_feedback_cross_project_api_key_rejection(self):
        user = User.objects.create_user(username="crossuser", password="password")
        proj_a = Project.objects.create(project_id="proj_a", display_name="Project A", user=user)
        proj_b = Project.objects.create(project_id="proj_b", display_name="Project B", user=user)
        key_a = APIKey.objects.create(user=user, project=proj_a, name="Key A")

        client = Client()
        # Attempt to post feedback for Project B using Key A
        response = client.post(
            "/rag/api/chatbot/feedback/",
            data=json.dumps({
                "store_id": "proj_b",
                "message_id": "msg_cross",
                "value": "up"
            }),
            content_type="application/json",
            HTTP_X_API_KEY=key_a.key
        )

        assert response.status_code == 403
        assert "not authorized for this project" in response.json()["error"]


@pytest.mark.django_db
class TestProjectFeedbackHTMXView:
    """Tests for Project Admin Feedback tab HTMX view and metrics"""

    def test_project_feedback_metrics_calculation(self):
        user = User.objects.create_user(username="fbadmin", password="password")
        project = Project.objects.create(
            project_id="postgres_metrics_proj",
            display_name="Metrics Project",
            storage_type="postgres",
            user=user
        )

        # 3 Up, 1 Down
        ChatFeedback.objects.create(project=project, message_id="m1", value="up", customer_id="1")
        ChatFeedback.objects.create(project=project, message_id="m2", value="up", customer_id="2")
        ChatFeedback.objects.create(project=project, message_id="m3", value="up", customer_id="3")
        ChatFeedback.objects.create(project=project, message_id="m4", value="down", customer_id="4")

        factory = RequestFactory()
        request = factory.get(f"/rag/projects/{project.project_id}/feedback/")
        request.user = user

        response = project_feedback(request, store_id=project.project_id)
        assert response.status_code == 200
        content = response.content.decode("utf-8")

        assert "Customer Chatbot Feedback" in content
        assert "Total Feedback Received" in content
        assert "75.0%" in content  # 3/4 = 75%
        assert "25.0%" in content  # 1/4 = 25%
        assert "m1" in content
        assert "m4" in content
