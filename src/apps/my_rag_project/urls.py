"""
URL configuration for my_rag_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
"""
from django.contrib import admin
from django.urls import path, include
from src.apps.my_rag_project.admin import custom_admin_site
from src.apps.chat.views import chat as chat_api_view

urlpatterns = [
    # Custom Unfold Admin Site
    path('dashboard/', custom_admin_site.urls),
    # Admin at root level
    path('admin/', admin.site.urls),
    # Auth routes at root level
    path('accounts/', include('django.contrib.auth.urls')),
    # Preserved DRF API routes
    path('rag/api/chat/', chat_api_view, name='chat_api'),
    path('rag/api/', include('src.apps.api.api_urls')),
    path('rag/', include('src.apps.documents.urls')),
]
