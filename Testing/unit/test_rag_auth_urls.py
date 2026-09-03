import pytest
from django.contrib.auth.models import User
from django.urls import resolve


@pytest.mark.django_db
def test_root_redirects_to_rag(client):
    response = client.get("/")
    assert response.status_code == 302
    assert response.url == "/rag/"


@pytest.mark.django_db
def test_rag_root_redirects_to_rag_login_for_unauthenticated_client(client):
    response = client.get("/rag/")

    assert response.status_code == 302
    assert response.url == "/rag/accounts/login/?next=/rag/"


def test_rag_login_route_exists():
    match = resolve("/rag/accounts/login/")

    assert match.url_name == "login"


@pytest.mark.django_db
def test_admin_login_redirects_to_django_admin_via_accounts_login(client):
    admin_user = User.objects.create_superuser(
        username="admin_user",
        email="admin@example.com",
        password="AdminPassword123!"
    )
    response = client.post("/rag/accounts/login/", {
        "username": "admin_user",
        "password": "AdminPassword123!"
    })

    assert response.status_code == 302
    assert response.url == "/rag/admin/"


@pytest.mark.django_db
def test_regular_user_login_redirects_to_dashboard_via_accounts_login(client):
    regular_user = User.objects.create_user(
        username="regular_user",
        email="user@example.com",
        password="UserPassword123!"
    )
    response = client.post("/rag/accounts/login/", {
        "username": "regular_user",
        "password": "UserPassword123!"
    })

    assert response.status_code == 302
    assert response.url == "/rag/dashboard/"


@pytest.mark.django_db
def test_admin_login_redirects_to_django_admin_via_dashboard_login(client):
    admin_user = User.objects.create_superuser(
        username="dashboard_admin",
        email="dash_admin@example.com",
        password="AdminPassword123!"
    )
    response = client.post("/rag/unfold/login/?next=/rag/unfold/", {
        "username": "dashboard_admin",
        "password": "AdminPassword123!"
    })

    assert response.status_code == 302
    assert response.url == "/rag/admin/"


@pytest.mark.django_db
def test_regular_user_login_redirects_to_dashboard_via_dashboard_login(client):
    regular_user = User.objects.create_user(
        username="dashboard_user",
        email="dash_user@example.com",
        password="UserPassword123!"
    )
    response = client.post("/rag/unfold/login/?next=/rag/unfold/", {
        "username": "dashboard_user",
        "password": "UserPassword123!"
    })

    assert response.status_code == 302
    assert response.url == "/rag/dashboard/"


@pytest.mark.django_db
def test_authenticated_admin_visiting_rag_root_redirects_to_django_admin(client):
    admin_user = User.objects.create_superuser(
        username="logged_admin",
        email="logged_admin@example.com",
        password="AdminPassword123!"
    )
    client.force_login(admin_user)
    response = client.get("/rag/")

    assert response.status_code == 302
    assert response.url == "/rag/admin/"


@pytest.mark.django_db
def test_authenticated_regular_user_visiting_rag_root_redirects_to_dashboard(client):
    regular_user = User.objects.create_user(
        username="logged_user",
        email="logged_user@example.com",
        password="UserPassword123!"
    )
    client.force_login(regular_user)
    response = client.get("/rag/")

    assert response.status_code == 302
    assert response.url == "/rag/dashboard/"