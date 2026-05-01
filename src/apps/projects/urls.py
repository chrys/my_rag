"""
URL routing for projects app (pages only)
"""

from django.urls import path
from . import views

app_name = 'projects'

# API endpoints are handled by apps/api/api_urls.py
# Page routes for HTML rendering
urlpatterns = [
    path('list/', views.list_projects, name='list'),
    path('create/', views.create_project, name='create'),
    path('delete/<str:store_id>/', views.delete_project, name='delete'),
]
