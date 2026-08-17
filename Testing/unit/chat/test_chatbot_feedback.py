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
from src.apps.projects.views import project_feedback, export_feedback_csv


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
        ChatFeedback.objects.create(
            project=project,
            message_id="m1",
            value="up",
            customer_id="cust_101",
            query="What are the venue rental prices?",
            reply="The venue rental is 2500 EUR."
        )
        ChatFeedback.objects.create(
            project=project,
            message_id="m2",
            value="up",
            customer_id="cust_102",
            query="Can we bring outside wine?",
            reply="Yes, corkage fee applies."
        )
        ChatFeedback.objects.create(
            project=project,
            message_id="m3",
            value="up",
            customer_id="cust_103"
        )
        ChatFeedback.objects.create(
            project=project,
            message_id="m4",
            value="down",
            customer_id="cust_104",
            query="Is parking free?",
            reply="Parking is 10 EUR/day."
        )

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
        assert "cust_101" in content
        assert "What are the venue rental prices?" in content
        assert "The venue rental is 2500 EUR." in content
        assert "Is parking free?" in content

    def test_feedback_with_query_and_reply_payload(self):
        user = User.objects.create_user(username="qruser", password="password")
        project = Project.objects.create(
            project_id="postgres_qr_proj",
            display_name="QR Project",
            storage_type="postgres",
            user=user
        )

        client = Client()
        payload = {
            "store_id": "postgres_qr_proj",
            "message_id": "msg_qr_001",
            "value": "up",
            "customer_id": "cust_55",
            "query": "How many guests can we invite?",
            "reply": "The venue capacity is up to 150 guests.",
            "timestamp": "2026-08-17T08:00:00+00:00"
        }

        response = client.post(
            "/rag/api/chatbot/feedback/",
            data=json.dumps(payload),
            content_type="application/json"
        )

        assert response.status_code == 201
        data = response.json()
        assert data["query"] == "How many guests can we invite?"
        assert data["reply"] == "The venue capacity is up to 150 guests."

        fb = ChatFeedback.objects.get(id=data["feedback_id"])
        assert fb.query == "How many guests can we invite?"
        assert fb.reply == "The venue capacity is up to 150 guests."

    def test_project_feedback_filter_by_client_datetime(self):
        import datetime
        from django.utils import timezone
        user = User.objects.create_user(username="datefilteruser", password="password")
        project = Project.objects.create(
            project_id="postgres_date_filter_proj",
            display_name="Date Filter Project",
            storage_type="postgres",
            user=user
        )

        # Day 1: 2026-08-10
        t1 = timezone.make_aware(datetime.datetime(2026, 8, 10, 10, 0, 0))
        ChatFeedback.objects.create(
            project=project,
            message_id="m_aug10",
            value="up",
            customer_id="cust_aug10",
            query="Aug 10 query",
            timestamp=t1
        )

        # Day 2: 2026-08-15
        t2 = timezone.make_aware(datetime.datetime(2026, 8, 15, 14, 30, 0))
        ChatFeedback.objects.create(
            project=project,
            message_id="m_aug15",
            value="down",
            customer_id="cust_aug15",
            query="Aug 15 query",
            timestamp=t2
        )

        # Day 3: 2026-08-20
        t3 = timezone.make_aware(datetime.datetime(2026, 8, 20, 9, 15, 0))
        ChatFeedback.objects.create(
            project=project,
            message_id="m_aug20",
            value="up",
            customer_id="cust_aug20",
            query="Aug 20 query",
            timestamp=t3
        )

        factory = RequestFactory()

        # Filter between 2026-08-12 and 2026-08-16 -> should only match Aug 15
        request = factory.get(
            f"/rag/projects/{project.project_id}/feedback/",
            {"start_date": "2026-08-12", "end_date": "2026-08-16"}
        )
        request.user = user

        response = project_feedback(request, store_id=project.project_id)
        assert response.status_code == 200
        content = response.content.decode("utf-8")

        assert "cust_aug15" in content
        assert "Aug 15 query" in content
        assert "cust_aug10" not in content
        assert "cust_aug20" not in content

    def test_export_feedback_csv_all_and_filtered(self):
        import datetime
        from django.utils import timezone
        user = User.objects.create_user(username="csvexportuser", password="password")
        project = Project.objects.create(
            project_id="postgres_csv_export_proj",
            display_name="CSV Export Project",
            storage_type="postgres",
            user=user
        )

        t1 = timezone.make_aware(datetime.datetime(2026, 8, 1, 10, 0, 0))
        t2 = timezone.make_aware(datetime.datetime(2026, 8, 15, 12, 0, 0))

        ChatFeedback.objects.create(
            project=project,
            message_id="msg_csv_1",
            value="up",
            customer_id="cust_1",
            query="Pricing info?",
            reply="Prices start at 100.",
            timestamp=t1
        )
        ChatFeedback.objects.create(
            project=project,
            message_id="msg_csv_2",
            value="down",
            customer_id="cust_2",
            query="Cancellation policy?",
            reply="No refunds.",
            timestamp=t2
        )

        factory = RequestFactory()

        # 1. Export all
        req_all = factory.get(f"/rag/projects/{project.project_id}/feedback/export-csv/")
        req_all.user = user
        res_all = export_feedback_csv(req_all, store_id=project.project_id)

        assert res_all.status_code == 200
        assert "text/csv" in res_all["Content-Type"]
        assert f"attachment; filename=\"feedback_{project.project_id}_" in res_all["Content-Disposition"]
        body_all = res_all.content.decode("utf-8")
        assert "Feedback,Customer ID,Client Timestamp,Recorded At,Query,Reply,Message ID,Conversation ID" in body_all
        assert "Pricing info?" in body_all
        assert "Cancellation policy?" in body_all
        assert "cust_1" in body_all
        assert "cust_2" in body_all

        # 2. Export filtered by rating=up
        req_filtered = factory.get(f"/rag/projects/{project.project_id}/feedback/export-csv/", {"rating": "up"})
        req_filtered.user = user
        res_filtered = export_feedback_csv(req_filtered, store_id=project.project_id)

        assert res_filtered.status_code == 200
        body_filtered = res_filtered.content.decode("utf-8")
        assert "Pricing info?" in body_filtered
        assert "Cancellation policy?" not in body_filtered



