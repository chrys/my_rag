"""
Custom DRF Permission classes for Role-Based Access Control (RBAC)
"""

from rest_framework.permissions import BasePermission, SAFE_METHODS
from rest_framework.request import Request
from rest_framework.views import APIView


class IsAdminUserOnly(BasePermission):
    """
    Allows access only to staff or superuser administrators for all HTTP methods.
    """
    message = "You do not have permission to perform this action. Administrator privileges required."

    def has_permission(self, request: Request, view: APIView) -> bool:
        user = request.user
        return bool(user and user.is_authenticated and (getattr(user, "is_staff", False) or getattr(user, "is_superuser", False)))


class IsAdminOrProjectReadOnly(BasePermission):
    """
    Allows read-only access (GET/HEAD/OPTIONS) to authenticated users,
    while write operations (POST/PUT/PATCH/DELETE) are restricted strictly to staff or superusers.
    """
    message = "You do not have permission to perform this action. Administrator privileges required."

    def has_permission(self, request: Request, view: APIView) -> bool:
        user = request.user
        if not user or not user.is_authenticated:
            return False

        if request.method in SAFE_METHODS:
            return True

        return bool(getattr(user, "is_staff", False) or getattr(user, "is_superuser", False))
