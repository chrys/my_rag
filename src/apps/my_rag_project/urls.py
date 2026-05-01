"""
URL configuration for my_rag_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    # Admin at root level
    path('admin/', admin.site.urls),
    # Auth routes at root level
    path('accounts/', include('django.contrib.auth.urls')),
    # RAG Dashboard routes (prefixed with /rag/)
    path('rag/', include([
        path('accounts/', include('django.contrib.auth.urls')),
        path('api/', include('src.apps.api.api_urls')),
        path('', include('src.apps.chat.urls')),
        path('', include('src.apps.projects.urls')),
        path('', include('src.apps.documents.urls')),
        path('', include('src.apps.evaluate.urls')),
    ])),
]
