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
    """Admin dashboard - redirects admins to Django admin, regular users to Pico.css dashboard"""
    if request.user.is_staff or request.user.is_superuser:
        return redirect('/rag/admin/')
    return redirect('/rag/dashboard/')


@login_required
@require_http_methods(["GET"])
def chat_page(request):
    """Chat interface - redirects admins to admin chat workflow, regular users to Pico.css chat tab"""
    if request.user.is_staff or request.user.is_superuser:
        return redirect('/rag/unfold/chat/')
    return redirect('/rag/dashboard/?tab=chat')


@login_required
@require_http_methods(["GET"])
def evaluate_page(request):
    """Evaluation interface - redirects admins to admin evaluation workflow, regular users to Pico.css evaluate tab"""
    if request.user.is_staff or request.user.is_superuser:
        return redirect('/rag/unfold/evaluate/')
    return redirect('/rag/dashboard/?tab=evaluate')

