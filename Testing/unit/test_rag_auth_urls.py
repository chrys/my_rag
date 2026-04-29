import pytest
from django.urls import resolve


@pytest.mark.django_db
def test_rag_root_redirects_to_rag_login_for_unauthenticated_client(client):
    response = client.get("/rag/")

    assert response.status_code == 302
    assert response.url == "/rag/accounts/login/?next=/rag/"


def test_rag_login_route_exists():
    match = resolve("/rag/accounts/login/")

    assert match.url_name == "login"