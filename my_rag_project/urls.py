"""
URL configuration for my_rag_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    # RAG Dashboard routes (prefixed with /rag/)
    path('rag/', include([
        path('admin/', admin.site.urls),
        path('accounts/', include('django.contrib.auth.urls')),
        path('api/', include('apps.api.api_urls')),
        path('', include('apps.chat.urls')),
        path('', include('apps.projects.urls')),
        path('', include('apps.documents.urls')),
        path('', include('apps.evaluate.urls')),
    ])),
]
