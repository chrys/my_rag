"""
Unit tests for Custom RBAC DRF Permission Classes
"""

import pytest
from django.contrib.auth.models import User, AnonymousUser
from rest_framework.test import APIRequestFactory
from rest_framework.views import APIView
from rest_framework.permissions import SAFE_METHODS

from src.apps.api.permissions import IsAdminUserOnly, IsAdminOrProjectReadOnly


@pytest.fixture
def factory():
    return APIRequestFactory()


@pytest.fixture
def regular_user(db):
    return User.objects.create_user(username="regular_user", password="password123")


@pytest.fixture
def staff_user(db):
    return User.objects.create_user(username="staff_user", password="password123", is_staff=True)


@pytest.fixture
def superuser(db):
    return User.objects.create_superuser(username="superuser", password="password123")


@pytest.mark.django_db
class TestIsAdminUserOnly:
    def test_unauthenticated_user_rejected(self, factory):
        request = factory.get("/api/test/")
        request.user = AnonymousUser()
        permission = IsAdminUserOnly()
        assert permission.has_permission(request, APIView()) is False

    def test_regular_authenticated_user_rejected(self, factory, regular_user):
        for method in ["get", "post", "put", "patch", "delete"]:
            request = getattr(factory, method)("/api/test/")
            request.user = regular_user
            permission = IsAdminUserOnly()
            assert permission.has_permission(request, APIView()) is False

    def test_staff_user_allowed(self, factory, staff_user):
        for method in ["get", "post", "put", "patch", "delete"]:
            request = getattr(factory, method)("/api/test/")
            request.user = staff_user
            permission = IsAdminUserOnly()
            assert permission.has_permission(request, APIView()) is True

    def test_superuser_allowed(self, factory, superuser):
        for method in ["get", "post", "put", "patch", "delete"]:
            request = getattr(factory, method)("/api/test/")
            request.user = superuser
            permission = IsAdminUserOnly()
            assert permission.has_permission(request, APIView()) is True


@pytest.mark.django_db
class TestIsAdminOrProjectReadOnly:
    def test_unauthenticated_user_rejected(self, factory):
        request = factory.get("/api/projects/")
        request.user = AnonymousUser()
        permission = IsAdminOrProjectReadOnly()
        assert permission.has_permission(request, APIView()) is False

    def test_regular_user_safe_methods_allowed(self, factory, regular_user):
        for method in ["get", "head", "options"]:
            request = getattr(factory, method)("/api/projects/")
            request.user = regular_user
            permission = IsAdminOrProjectReadOnly()
            assert permission.has_permission(request, APIView()) is True

    def test_regular_user_unsafe_methods_rejected(self, factory, regular_user):
        for method in ["post", "put", "patch", "delete"]:
            request = getattr(factory, method)("/api/projects/")
            request.user = regular_user
            permission = IsAdminOrProjectReadOnly()
            assert permission.has_permission(request, APIView()) is False

    def test_staff_user_all_methods_allowed(self, factory, staff_user):
        for method in ["get", "post", "put", "patch", "delete"]:
            request = getattr(factory, method)("/api/projects/")
            request.user = staff_user
            permission = IsAdminOrProjectReadOnly()
            assert permission.has_permission(request, APIView()) is True

    def test_superuser_all_methods_allowed(self, factory, superuser):
        for method in ["get", "post", "put", "patch", "delete"]:
            request = getattr(factory, method)("/api/projects/")
            request.user = superuser
            permission = IsAdminOrProjectReadOnly()
            assert permission.has_permission(request, APIView()) is True
