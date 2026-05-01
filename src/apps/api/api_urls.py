from django.urls import path, include, re_path
from rest_framework.routers import DefaultRouter
from src.apps.projects.api_views import ProjectViewSet, SystemPromptViewSet
from src.apps.documents.api_views import DocumentViewSet
from src.apps.documents.views import delete_document
from src.apps.chat.api_views import ChatMessageViewSet
from src.apps.evaluate.api_views import EvaluationDatasetViewSet, EvaluationResultViewSet
from src.apps.api.api_views import APIKeyViewSet, APIUsageViewSet

# Create router and register viewsets
router = DefaultRouter()

# Register ProjectViewSet with custom lookup regex to accept slashes
router.register(r'projects', ProjectViewSet, basename='project')
router.register(r'prompts', SystemPromptViewSet, basename='prompt')
router.register(r'documents', DocumentViewSet, basename='document')
router.register(r'messages', ChatMessageViewSet, basename='message')
router.register(r'datasets', EvaluationDatasetViewSet, basename='dataset')
router.register(r'results', EvaluationResultViewSet, basename='result')
router.register(r'keys', APIKeyViewSet, basename='apikey')
router.register(r'usage', APIUsageViewSet, basename='apiusage')

app_name = 'api'

urlpatterns = [
    # Must come BEFORE router.urls — the DRF router splits 'file.txt' into pk + format suffix
    # so filenames with dots never reach get_object(). This explicit route catches them first.
    re_path(r'^documents/(?P<document_id>[^/]+\.[^/]+)$', delete_document, name='document-delete'),
    path('', include(router.urls)),
]
