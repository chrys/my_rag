"""
URL routing for documents app
"""
from django.urls import path
from . import views

app_name = 'documents'

urlpatterns = [
    path('documents/<str:store_id>/', views.list_documents, name='list'),
    path('documents/<str:store_id>/upload/', views.upload_document, name='upload'),
    path('documents/<str:store_id>/inspect/', views.inspect_document, name='inspect_document_alt'),
    path('projects/<str:store_id>/inspect-document/', views.inspect_document, name='inspect_document'),
    path('projects/<str:store_id>/set-source-type/', views.set_source_type, name='set_source_type'),
    path('projects/<str:store_id>/obsidian/save-path/', views.obsidian_save_path, name='obsidian_save_path'),
    path('projects/<str:store_id>/obsidian/index/', views.obsidian_index, name='obsidian_index'),
    path('projects/<str:store_id>/obsidian/index-new/', views.obsidian_index_new, name='obsidian_index_new'),
    path('projects/<str:store_id>/obsidian/sync/', views.obsidian_sync, name='obsidian_sync'),
    path('projects/<str:store_id>/obsidian/status/', views.obsidian_status, name='obsidian_status'),
    path('projects/<str:store_id>/google-calendar/connect/', views.google_calendar_connect, name='google_calendar_connect'),
    path('projects/<str:store_id>/google-calendar/preferences/', views.google_calendar_save_preferences, name='google_calendar_save_preferences'),
    path('projects/<str:store_id>/google-calendar/sync/', views.google_calendar_sync, name='google_calendar_sync'),
    path('projects/<str:store_id>/google-calendar/index-new/', views.google_calendar_index_new, name='google_calendar_index_new'),
    path('projects/<str:store_id>/google-calendar/full-reindex/', views.google_calendar_full_reindex, name='google_calendar_full_reindex'),
    path('projects/<str:store_id>/google-calendar/status/', views.google_calendar_status, name='google_calendar_status'),
    path('google/oauth2callback/', views.google_calendar_oauth_callback, name='google_calendar_oauth_callback'),
]
