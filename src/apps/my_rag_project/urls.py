"""
URL configuration for my_rag_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
"""
from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from src.apps.my_rag_project.admin import custom_admin_site, CustomLoginView
from src.apps.chat.views import chat as chat_api_view, chatbot_feedback as feedback_api_view

urlpatterns = [
    # Root path redirect to /rag/
    path('', RedirectView.as_view(url='/rag/', permanent=False)),
    # Custom Unfold Admin Site under /rag/unfold/ and /rag/admin/
    path('rag/unfold/', custom_admin_site.urls),
    # Admin at root level under /rag/admin/
    path('rag/admin/', admin.site.urls),
    # Custom login route before default auth urls
    path('rag/accounts/login/', CustomLoginView.as_view(), name='login'),
    # Auth routes under /rag/
    path('rag/accounts/', include('django.contrib.auth.urls')),
    # Preserved DRF API routes
    path('rag/api/chat/', chat_api_view, name='chat_api'),
    path('rag/api/chatbot/feedback/', feedback_api_view, name='chatbot_feedback'),
    path('rag/api/feedback/', feedback_api_view, name='rag_api_feedback'),
    path('rag/chatbot/feedback/', feedback_api_view, name='rag_chatbot_feedback'),
    path('api/chatbot/feedback/', feedback_api_view, name='chatbot_feedback_direct'),
    path('rag/api/', include('src.apps.api.api_urls')),
    path('api/', include('src.apps.api.api_urls')),
    path('rag/', include('src.apps.documents.urls')),
    path('rag/', include('src.apps.projects.urls')),
    path('rag/', include('src.apps.chat.urls')),
    path('rag/', include('src.apps.evaluate.urls')),
]

from django.http import JsonResponse

def custom_error_403(request, exception=None):
    return JsonResponse({'error': 'Forbidden'}, status=403)

def custom_error_404(request, exception=None):
    return JsonResponse({'error': 'Not Found'}, status=404)

def custom_error_500(request):
    return JsonResponse({'error': 'Internal Server Error'}, status=500)

handler403 = custom_error_403
handler404 = custom_error_404
handler500 = custom_error_500
