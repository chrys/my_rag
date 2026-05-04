"""
URL routing for documents app
"""
from django.urls import path
from . import views

app_name = 'documents'

urlpatterns = [
    path('documents/<str:store_id>/', views.list_documents, name='list'),
    path('documents/<str:store_id>/upload/', views.upload_document, name='upload'),
]
