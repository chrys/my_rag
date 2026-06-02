"""
Page views for template rendering
"""

from django.shortcuts import redirect
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required


@login_required
@require_http_methods(["GET"])
def index(request):
    """Home page - redirects to unfold dashboard"""
    return redirect('/rag/dashboard/')


@login_required
@require_http_methods(["GET"])
def admin_page(request):
    """Admin dashboard - redirects to unfold dashboard"""
    return redirect('/rag/dashboard/')


@login_required
@require_http_methods(["GET"])
def chat_page(request):
    """Chat interface - redirects to unfold chat panel"""
    return redirect('/rag/dashboard/chat/')


@login_required
@require_http_methods(["GET"])
def evaluate_page(request):
    """Redirect to evaluation dashboard panel"""
    return redirect('/rag/dashboard/evaluate/')

