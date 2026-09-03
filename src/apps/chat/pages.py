"""
Page views for template rendering
"""

from django.shortcuts import redirect
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required


@login_required
@require_http_methods(["GET"])
def index(request):
    """Home page - redirects to Django admin for admin users and Pico.css dashboard for regular users"""
    if request.user.is_staff or request.user.is_superuser:
        return redirect('/rag/admin/')
    return redirect('/rag/dashboard/')


@login_required
@require_http_methods(["GET"])
def admin_page(request):
    """Admin dashboard - redirects to Pico.css dashboard"""
    return redirect('/rag/dashboard/')


@login_required
@require_http_methods(["GET"])
def chat_page(request):
    """Chat interface - redirects to chat tab on dashboard"""
    return redirect('/rag/dashboard/?tab=chat')


@login_required
@require_http_methods(["GET"])
def evaluate_page(request):
    """Redirect to evaluation tab on dashboard"""
    return redirect('/rag/dashboard/?tab=evaluate')

