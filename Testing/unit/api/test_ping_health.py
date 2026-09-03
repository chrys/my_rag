import pytest
from django.test import Client
from django.contrib.auth.models import User
from src.apps.api.models import APIKey
from src.apps.projects.models import Project


@pytest.mark.django_db
class TestPingAndHealthEndpoints:
    def test_ping_without_key_returns_403(self, client: Client):
        res = client.get("/api/ping/")
        assert res.status_code == 403
        data = res.json()
        assert data["status"] == "forbidden"
        assert "Invalid or missing health key" in data["error"]

    def test_ping_with_invalid_key_returns_403(self, client: Client):
        res = client.get("/api/ping/", HTTP_X_HEALTH_KEY="wrong-secret")
        assert res.status_code == 403
        data = res.json()
        assert data["status"] == "forbidden"

    def test_ping_with_valid_header_key_returns_200(self, client: Client):
        res = client.get("/api/ping/", HTTP_X_HEALTH_KEY="rag-health-secret-key")
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "ok"
        assert data["message"] == "pong"
        assert data["service"] == "my_rag"
        assert "timestamp" in data

    def test_ping_with_query_param_returns_200(self, client: Client):
        res = client.get("/api/ping/?key=rag-health-secret-key")
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "ok"
        assert data["message"] == "pong"

    def test_ping_with_bearer_token_returns_200(self, client: Client):
        res = client.get("/api/ping/", HTTP_AUTHORIZATION="Bearer rag-health-secret-key")
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "ok"
        assert data["message"] == "pong"

    def test_ping_under_rag_prefix_returns_200(self, client: Client):
        res = client.get("/rag/api/ping/?key=rag-health-secret-key")
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "ok"
        assert data["message"] == "pong"

    def test_ping_with_active_api_key_returns_200(self, client: Client):
        user = User.objects.create_user(username="pingtestuser", password="password123")
        api_key = APIKey.objects.create(
            user=user,
            name="Test Ping Key",
            key="api_key_secret_ping_123",
            is_active=True
        )
        res = client.get("/api/ping/", HTTP_X_HEALTH_KEY="api_key_secret_ping_123")
        assert res.status_code == 200
        assert res.json()["status"] == "ok"

    def test_health_with_valid_key_returns_database_status(self, client: Client):
        res = client.get("/api/health/?key=rag-health-secret-key")
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "healthy"
        assert data["database"] == "connected"
        assert data["service"] == "my_rag"

        # Second call within 15s should be cached
        res2 = client.get("/api/health/?key=rag-health-secret-key")
        assert res2.status_code == 200
        data2 = res2.json()
        assert data2["database"] == "connected"
        assert data2["cached"] is True
