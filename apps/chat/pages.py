"""
Page views for template rendering
"""

from django.shortcuts import render
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required


@login_required
@require_http_methods(["GET"])
def index(request):
    """Home page - renders admin dashboard"""
    context = {'url_prefix': ''}
    return render(request, 'projects/admin.html', context)


@login_required
@require_http_methods(["GET"])
def admin_page(request):
    """Admin dashboard - can be loaded via HTMX or directly"""
    context = {'url_prefix': ''}
    return render(request, 'projects/admin.html', context)


@login_required
@require_http_methods(["GET"])
def chat_page(request):
    """Chat interface"""
    return render(request, 'chat/chat.html')


@login_required
@require_http_methods(["GET"])
def evaluate_page(request):
    """Evaluation interface"""
    return render(request, 'evaluate/evaluate.html')
