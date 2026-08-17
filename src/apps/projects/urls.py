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
    path('projects/<str:store_id>/api-keys/', views.project_api_keys, name='project_api_keys'),
    path('projects/<str:store_id>/api-keys/create/', views.create_project_api_key, name='create_project_api_key'),
    path('projects/<str:store_id>/api-keys/<int:key_id>/toggle/', views.toggle_project_api_key, name='toggle_project_api_key'),
    path('projects/<str:store_id>/api-keys/<int:key_id>/delete/', views.delete_project_api_key, name='delete_project_api_key'),
    path('projects/<str:store_id>/feedback/', views.project_feedback, name='project_feedback'),
    path('projects/<str:store_id>/feedback/export-csv/', views.export_feedback_csv, name='export_feedback_csv'),
]

