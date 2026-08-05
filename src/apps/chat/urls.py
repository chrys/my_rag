"""
URL routing for chat app (pages only)
"""

from django.urls import path
from . import pages, views

app_name = 'chat'

urlpatterns = [
    path('', pages.index, name='index'),
    path('dashboard/', pages.admin_page, name='admin'),
    path('chat/', pages.chat_page, name='chat_page'),
    path('evaluate/', pages.evaluate_page, name='evaluate_page'),
    path('submit/', views.chat_submit, name='submit'),
    # API endpoints are registered in apps/api/api_urls.py
]
