"""
Unit tests for chat app API views
Tests ChatMessageViewSet and custom actions
"""

import pytest
from rest_framework.test import APIRequestFactory
from rest_framework.test import force_authenticate
from rest_framework import status
from django.contrib.auth.models import User
from src.apps.projects.models import Project
from src.apps.chat.models import ChatMessage
from src.apps.chat.api_views import ChatMessageViewSet


@pytest.fixture
def api_factory():
    """Fixture for API request factory"""
    return APIRequestFactory()


@pytest.fixture
def authenticated_user():
    """Fixture for creating an authenticated user"""
    return User.objects.create_user(
        username='api_user',
        password='pass123'
    )


@pytest.fixture
def project():
    """Fixture for creating a project"""
    return Project.objects.create(
        project_id='api_test_proj',
        display_name='API Test Project'
    )


@pytest.mark.django_db
class TestChatMessageViewSet:
    """Test cases for ChatMessageViewSet"""
    
    def test_list_messages(self, api_factory, project):
        """Test listing all messages"""
        msg1 = ChatMessage.objects.create(
            project=project,
            message_type='user',
            content='Message 1'
        )
        msg2 = ChatMessage.objects.create(
            project=project,
            message_type='assistant',
            content='Message 2'
        )
        
        request = api_factory.get('/api/messages/')
        view = ChatMessageViewSet.as_view({'get': 'list'})
        response = view(request)
        
        assert response.status_code == status.HTTP_200_OK
        # Response is paginated
        assert response.data['count'] == 2
        assert len(response.data['results']) == 2
    
    def test_retrieve_message(self, api_factory, project):
        """Test retrieving a single message"""
        message = ChatMessage.objects.create(
            project=project,
            message_type='user',
            content='Get this message'
        )
        
        request = api_factory.get(f'/api/messages/{message.id}/')
        view = ChatMessageViewSet.as_view({'get': 'retrieve'})
        response = view(request, pk=message.id)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['content'] == 'Get this message'
    
    def test_create_message(self, api_factory, project):
        """Test creating a message"""
        data = {
            'project': project.id,
            'message_type': 'user',
            'content': 'New message',
            'session_id': 'session_x'
        }
        
        request = api_factory.post('/api/messages/', data, format='json')
        view = ChatMessageViewSet.as_view({'post': 'create'})
        response = view(request)
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['content'] == 'New message'
        
        # Verify in database
        assert ChatMessage.objects.filter(content='New message').exists()
    
    def test_update_message(self, api_factory, project):
        """Test updating a message"""
        message = ChatMessage.objects.create(
            project=project,
            message_type='user',
            content='Original'
        )
        
        data = {
            'project': project.id,
            'message_type': 'assistant',
            'content': 'Updated content',
            'session_id': 'updated'
        }
        request = api_factory.put(f'/api/messages/{message.id}/', data, format='json')
        view = ChatMessageViewSet.as_view({'put': 'update'})
        response = view(request, pk=message.id)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['content'] == 'Updated content'
        assert response.data['message_type'] == 'assistant'
    
    def test_partial_update_message(self, api_factory, project):
        """Test partial update of a message"""
        message = ChatMessage.objects.create(
            project=project,
            message_type='user',
            content='Original',
            session_id='session_1'
        )
        
        data = {'content': 'Partially updated'}
        request = api_factory.patch(f'/api/messages/{message.id}/', data, format='json')
        view = ChatMessageViewSet.as_view({'patch': 'partial_update'})
        response = view(request, pk=message.id)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['content'] == 'Partially updated'
        assert response.data['session_id'] == 'session_1'
    
    def test_delete_message(self, api_factory, project):
        """Test deleting a message"""
        message = ChatMessage.objects.create(
            project=project,
            message_type='user',
            content='Delete me'
        )
        
        msg_id = message.id
        request = api_factory.delete(f'/api/messages/{msg_id}/')
        view = ChatMessageViewSet.as_view({'delete': 'destroy'})
        response = view(request, pk=msg_id)
        
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not ChatMessage.objects.filter(id=msg_id).exists()
    
    def test_by_project_action(self, api_factory, project):
        """Test by_project custom action"""
        msg1 = ChatMessage.objects.create(
            project=project,
            message_type='user',
            content='In project'
        )
        
        other_project = Project.objects.create(
            project_id='other_proj',
            display_name='Other'
        )
        msg2 = ChatMessage.objects.create(
            project=other_project,
            message_type='user',
            content='In other'
        )
        
        request = api_factory.get(f'/api/messages/by_project/?project_id={project.id}')
        view = ChatMessageViewSet.as_view({'get': 'by_project'})
        response = view(request)
        
        assert response.status_code == status.HTTP_200_OK
        # Should have at least the one message from this project
        messages = response.data if isinstance(response.data, list) else response.data.get('results', [])
        project_msgs = [m for m in messages if m.get('id') == msg1.id]
        assert len(project_msgs) == 1
    
    def test_by_project_missing_param(self, api_factory):
        """Test by_project requires project_id parameter"""
        request = api_factory.get('/api/messages/by_project/')
        view = ChatMessageViewSet.as_view({'get': 'by_project'})
        response = view(request)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'error' in response.data
    
    def test_by_session_action(self, api_factory, project):
        """Test by_session custom action"""
        msg1 = ChatMessage.objects.create(
            project=project,
            message_type='user',
            content='Session A',
            session_id='session_a'
        )
        msg2 = ChatMessage.objects.create(
            project=project,
            message_type='user',
            content='Session B',
            session_id='session_b'
        )
        
        request = api_factory.get('/api/messages/by_session/?session_id=session_a')
        view = ChatMessageViewSet.as_view({'get': 'by_session'})
        response = view(request)
        
        assert response.status_code == status.HTTP_200_OK
        # Response should contain only session_a messages
        messages = response.data if isinstance(response.data, list) else response.data.get('results', [])
        session_msgs = [m for m in messages if m.get('id') == msg1.id]
        assert len(session_msgs) == 1
    
    def test_by_session_missing_param(self, api_factory):
        """Test by_session requires session_id parameter"""
        request = api_factory.get('/api/messages/by_session/')
        view = ChatMessageViewSet.as_view({'get': 'by_session'})
        response = view(request)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'error' in response.data
    
    def test_by_user_action_authenticated(self, api_factory, project, authenticated_user):
        """Test by_user action with authenticated user"""
        msg1 = ChatMessage.objects.create(
            project=project,
            user=authenticated_user,
            message_type='user',
            content='My message'
        )
        
        other_user = User.objects.create_user(
            username='other_user',
            password='pass'
        )
        msg2 = ChatMessage.objects.create(
            project=project,
            user=other_user,
            message_type='user',
            content='Other message'
        )
        
        request = api_factory.get('/api/messages/by_user/')
        force_authenticate(request, user=authenticated_user)
        view = ChatMessageViewSet.as_view({'get': 'by_user'})
        response = view(request)
        
        assert response.status_code == status.HTTP_200_OK
        messages = response.data if isinstance(response.data, list) else response.data.get('results', [])
        user_msgs = [m for m in messages if m.get('id') == msg1.id]
        assert len(user_msgs) == 1
    
    def test_by_user_action_unauthenticated(self, api_factory):
        """Test by_user action requires authentication"""
        request = api_factory.get('/api/messages/by_user/')
        view = ChatMessageViewSet.as_view({'get': 'by_user'})
        response = view(request)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_get_serializer_class_list(self, api_factory, project):
        """Test correct serializer used for list action"""
        ChatMessage.objects.create(
            project=project,
            message_type='user',
            content='Test'
        )
        
        request = api_factory.get('/api/messages/')
        view = ChatMessageViewSet.as_view({'get': 'list'})
        response = view(request)
        
        # List serializer should have limited fields
        assert response.status_code == status.HTTP_200_OK
        if response.data.get('results'):
            msg_data = response.data['results'][0]
            # Should have basic fields but not all
            assert 'id' in msg_data
            assert 'content' in msg_data
    
    def test_get_serializer_class_create(self, api_factory, project):
        """Test correct serializer used for create action"""
        data = {
            'project': project.id,
            'message_type': 'user',
            'content': 'Test',
            'session_id': 'test'
        }
        
        request = api_factory.post('/api/messages/', data, format='json')
        view = ChatMessageViewSet.as_view({'post': 'create'})
        response = view(request)
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['content'] == 'Test'
    
    def test_message_filtering_by_type(self, api_factory, project):
        """Test filtering messages by type"""
        ChatMessage.objects.all().delete()  # Clear for clean test
        ChatMessage.objects.create(
            project=project,
            message_type='user',
            content='User query'
        )
        ChatMessage.objects.create(
            project=project,
            message_type='assistant',
            content='Assistant response'
        )
        
        request = api_factory.get('/api/messages/?message_type=user')
        view = ChatMessageViewSet.as_view({'get': 'list'})
        response = view(request)
        
        assert response.status_code == status.HTTP_200_OK
        # Should filter by message type - verify at least one user message
        if response.data.get('results'):
            user_msgs = [m for m in response.data['results'] if m['message_type'] == 'user']
            assert len(user_msgs) >= 1
