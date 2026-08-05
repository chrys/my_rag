"""
Unit tests for chat app serializers
Tests ChatMessage serializers with validation and data flow
"""

import pytest
from django.contrib.auth.models import User
from src.apps.projects.models import Project
from src.apps.chat.models import ChatMessage
from src.apps.chat.serializers import (
    ChatMessageSerializer,
    ChatMessageCreateSerializer,
    ChatMessageListSerializer,
    ChatResponseSerializer,
)


@pytest.fixture
def project():
    """Fixture for creating a project"""
    return Project.objects.create(
        project_id='serializer_test_proj',
        display_name='Serializer Test Project'
    )


@pytest.fixture
def user():
    """Fixture for creating a user"""
    return User.objects.create_user(
        username='serializer_user',
        password='pass123'
    )


@pytest.mark.django_db
class TestChatMessageSerializer:
    """Test ChatMessageSerializer"""
    
    def test_serialize_user_message(self, project, user) -> None:
        """Test serializing a user message"""
        message = ChatMessage.objects.create(
            project=project,
            user=user,
            message_type='user',
            content='What is this?',
            session_id='s1'
        )
        
        serializer = ChatMessageSerializer(message)
        data = serializer.data
        
        assert data['id'] == message.id
        assert data['project'] == project.id
        assert data['user'] == user.id
        assert data['user_username'] == 'serializer_user'
        assert data['message_type'] == 'user'
        assert data['content'] == 'What is this?'
    
    def test_serialize_assistant_message(self, project) -> None:
        """Test serializing an assistant message"""
        message = ChatMessage.objects.create(
            project=project,
            message_type='assistant',
            content='This is the answer',
            response_html='<p>This is the answer</p>',
            context_documents=[{'id': 1}]
        )
        
        serializer = ChatMessageSerializer(message)
        data = serializer.data
        
        assert data['message_type'] == 'assistant'
        assert data['content'] == 'This is the answer'
        assert data['response_html'] == '<p>This is the answer</p>'
        assert data['context_documents'] == [{'id': 1}]
    
    def test_serializer_read_only_fields(self, project) -> None:
        """Test that created_at and response_html are read-only"""
        message = ChatMessage.objects.create(
            project=project,
            message_type='user',
            content='Test'
        )
        
        serializer = ChatMessageSerializer(message)
        assert 'created_at' in serializer.data
        assert 'response_html' in serializer.data
        
        # Verify these fields are read-only
        assert 'created_at' in serializer.Meta.read_only_fields
        assert 'response_html' in serializer.Meta.read_only_fields
    
    def test_serialize_null_user(self, project) -> None:
        """Test serializing message with null user"""
        message = ChatMessage.objects.create(
            project=project,
            message_type='user',
            content='Anonymous query'
        )
        
        serializer = ChatMessageSerializer(message)
        assert serializer.data['user'] is None
        # When user is None, user_username will not be in the serializer output
        assert serializer.data.get('user_username') is None


@pytest.mark.django_db
class TestChatMessageCreateSerializer:
    """Test ChatMessageCreateSerializer"""
    
    def test_create_user_message(self, project) -> None:
        """Test creating message via serializer"""
        data = {
            'project': project.id,
            'message_type': 'user',
            'content': 'New query',
            'session_id': 'session_123'
        }
        
        serializer = ChatMessageCreateSerializer(data=data)
        assert serializer.is_valid()
        
        message = serializer.save()
        assert message.project.id == project.id
        assert message.message_type == 'user'
        assert message.content == 'New query'
        assert message.session_id == 'session_123'
    
    def test_create_required_fields(self, project) -> None:
        """Test required fields validation"""
        data = {
            'project': project.id,
            'message_type': 'user'
            # Missing content
        }
        
        serializer = ChatMessageCreateSerializer(data=data)
        assert not serializer.is_valid()
        assert 'content' in serializer.errors
    
    def test_create_optional_session_id(self, project) -> None:
        """Test session_id is optional"""
        data = {
            'project': project.id,
            'message_type': 'user',
            'content': 'Query without session'
        }
        
        serializer = ChatMessageCreateSerializer(data=data)
        assert serializer.is_valid()
        
        message = serializer.save()
        assert message.session_id == ''
    
    def test_create_invalid_message_type(self, project) -> None:
        """Test invalid message type is rejected"""
        data = {
            'project': project.id,
            'message_type': 'invalid',
            'content': 'Test'
        }
        
        serializer = ChatMessageCreateSerializer(data=data)
        assert not serializer.is_valid()
        assert 'message_type' in serializer.errors
    
    def test_create_valid_message_types(self, project) -> None:
        """Test both valid message types work"""
        for msg_type in ['user', 'assistant']:
            data = {
                'project': project.id,
                'message_type': msg_type,
                'content': f'{msg_type} message'
            }
            
            serializer = ChatMessageCreateSerializer(data=data)
            assert serializer.is_valid()


@pytest.mark.django_db
class TestChatMessageListSerializer:
    """Test ChatMessageListSerializer"""
    
    def test_list_serializer_fields(self, project) -> None:
        """Test list serializer has correct fields"""
        message = ChatMessage.objects.create(
            project=project,
            message_type='user',
            content='Query',
            session_id='s1'
        )
        
        serializer = ChatMessageListSerializer(message)
        data = serializer.data
        
        # Check included fields
        assert 'id' in data
        assert 'message_type' in data
        assert 'content' in data
        assert 'created_at' in data
        assert 'session_id' in data
        
        # Check excluded fields
        assert 'project' not in data
        assert 'user' not in data
        assert 'response_html' not in data
    
    def test_list_serializer_multiple(self, project) -> None:
        """Test serializing multiple messages"""
        msg1 = ChatMessage.objects.create(
            project=project,
            message_type='user',
            content='First'
        )
        msg2 = ChatMessage.objects.create(
            project=project,
            message_type='assistant',
            content='Second'
        )
        
        serializer = ChatMessageListSerializer(
            [msg1, msg2],
            many=True
        )
        
        assert len(serializer.data) == 2
        assert serializer.data[0]['content'] == 'First'
        assert serializer.data[1]['content'] == 'Second'


@pytest.mark.django_db
class TestChatResponseSerializer:
    """Test ChatResponseSerializer for API responses"""
    
    def test_serialize_response(self) -> None:
        """Test serializing chat response"""
        data = {
            'user_message': 'What is AI?',
            'bot_response': 'AI is artificial intelligence',
            'bot_response_html': '<p>AI is artificial intelligence</p>'
        }
        
        serializer = ChatResponseSerializer(data=data)
        assert serializer.is_valid()
    
    def test_response_required_fields(self) -> None:
        """Test response serializer requires all fields"""
        data = {
            'user_message': 'Question?',
            # Missing bot_response and bot_response_html
        }
        
        serializer = ChatResponseSerializer(data=data)
        assert not serializer.is_valid()
        assert 'bot_response' in serializer.errors
        assert 'bot_response_html' in serializer.errors
    
    def test_deserialize_response(self) -> None:
        """Test deserializing response for API output"""
        response_data = {
            'user_message': 'How are you?',
            'bot_response': 'I am well',
            'bot_response_html': '<p>I am well</p>'
        }
        
        serializer = ChatResponseSerializer(response_data)
        assert serializer.data == response_data
