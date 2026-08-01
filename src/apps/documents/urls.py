"""
URL routing for documents app
"""
from django.urls import path
from . import views

app_name = 'documents'

urlpatterns = [
    path('documents/<str:store_id>/', views.list_documents, name='list'),
    path('documents/<str:store_id>/upload/', views.upload_document, name='upload'),
    path('projects/<str:store_id>/set-source-type/', views.set_source_type, name='set_source_type'),
    path('projects/<str:store_id>/obsidian/save-path/', views.obsidian_save_path, name='obsidian_save_path'),
    path('projects/<str:store_id>/obsidian/index/', views.obsidian_index, name='obsidian_index'),
    path('projects/<str:store_id>/obsidian/index-new/', views.obsidian_index_new, name='obsidian_index_new'),
    path('projects/<str:store_id>/obsidian/sync/', views.obsidian_sync, name='obsidian_sync'),
    path('projects/<str:store_id>/obsidian/status/', views.obsidian_status, name='obsidian_status'),
]
