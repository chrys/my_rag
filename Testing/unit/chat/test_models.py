"""
Unit tests for chat app models
Tests ChatMessage model with relationships, timestamps, and constraints
"""

import pytest
from django.contrib.auth.models import User
from apps.projects.models import Project
from apps.chat.models import ChatMessage


@pytest.fixture
def authenticated_user():
    """Fixture for creating an authenticated user"""
    return User.objects.create_user(
        username='chatuser',
        password='chatpass123'
    )


@pytest.fixture
def project():
    """Fixture for creating a project"""
    return Project.objects.create(
        project_id='chat_test_proj',
        display_name='Chat Test Project'
    )


@pytest.mark.django_db
class TestChatMessageModel:
    """Test cases for ChatMessage model"""
    
    def test_create_user_message(self, project, authenticated_user):
        """Test creating a user chat message"""
        message = ChatMessage.objects.create(
            project=project,
            user=authenticated_user,
            message_type='user',
            content='Hello, what is the answer?',
            session_id='session_001'
        )
        
        assert message.id is not None
        assert message.project == project
        assert message.user == authenticated_user
        assert message.message_type == 'user'
        assert message.content == 'Hello, what is the answer?'
        assert message.session_id == 'session_001'
    
    def test_create_assistant_message(self, project):
        """Test creating an assistant chat message"""
        message = ChatMessage.objects.create(
            project=project,
            message_type='assistant',
            content='The answer is 42',
            response_html='<p>The answer is 42</p>',
            session_id='session_001'
        )
        
        assert message.message_type == 'assistant'
        assert message.content == 'The answer is 42'
        assert message.response_html == '<p>The answer is 42</p>'
        assert message.user is None
    
    def test_message_timestamps(self, project):
        """Test that messages have timestamps"""
        message = ChatMessage.objects.create(
            project=project,
            message_type='user',
            content='Test message'
        )
        
        assert message.created_at is not None
    
    def test_message_string_representation(self, project):
        """Test message string representation"""
        message = ChatMessage.objects.create(
            project=project,
            message_type='user',
            content='This is a test message for string representation'
        )
        
        str_repr = str(message)
        assert 'This is a test message' in str_repr
        assert 'User Message' in str_repr
    
    def test_message_string_representation_truncated(self, project):
        """Test message string representation with long content"""
        long_content = 'x' * 100
        message = ChatMessage.objects.create(
            project=project,
            message_type='user',
            content=long_content
        )
        
        str_repr = str(message)
        assert '...' in str_repr
        assert len(str_repr) < len(long_content)
    
    def test_context_documents_default(self, project):
        """Test context_documents defaults to empty list"""
        message = ChatMessage.objects.create(
            project=project,
            message_type='user',
            content='Query'
        )
        
        assert message.context_documents == []
        assert isinstance(message.context_documents, list)
    
    def test_context_documents_json(self, project):
        """Test storing JSON context documents"""
        docs = [
            {'id': 1, 'title': 'Doc 1', 'snippet': 'Content 1'},
            {'id': 2, 'title': 'Doc 2', 'snippet': 'Content 2'}
        ]
        message = ChatMessage.objects.create(
            project=project,
            message_type='user',
            content='Query',
            context_documents=docs
        )
        
        assert len(message.context_documents) == 2
        assert message.context_documents[0]['title'] == 'Doc 1'
    
    def test_system_prompt_stored(self, project):
        """Test storing system prompt with message"""
        prompt = "You are a helpful assistant."
        message = ChatMessage.objects.create(
            project=project,
            message_type='assistant',
            content='Response',
            system_prompt_used=prompt
        )
        
        assert message.system_prompt_used == prompt
    
    def test_session_id_blank(self, project):
        """Test session_id can be blank"""
        message = ChatMessage.objects.create(
            project=project,
            message_type='user',
            content='Query'
        )
        
        assert message.session_id == ''
    
    def test_message_ordering(self, project):
        """Test messages ordered by created_at descending"""
        msg1 = ChatMessage.objects.create(
            project=project,
            message_type='user',
            content='First'
        )
        msg2 = ChatMessage.objects.create(
            project=project,
            message_type='user',
            content='Second'
        )
        
        messages = ChatMessage.objects.all()
        assert messages[0].id == msg2.id
        assert messages[1].id == msg1.id
    
    def test_queryset_filter_by_project(self, project):
        """Test filtering messages by project"""
        other_project = Project.objects.create(
            project_id='other_proj',
            display_name='Other Project'
        )
        
        msg1 = ChatMessage.objects.create(
            project=project,
            message_type='user',
            content='In first project'
        )
        msg2 = ChatMessage.objects.create(
            project=other_project,
            message_type='user',
            content='In other project'
        )
        
        filtered = ChatMessage.objects.filter(project=project)
        assert filtered.count() == 1
        assert filtered.first().id == msg1.id
    
    def test_queryset_filter_by_session(self, project):
        """Test filtering messages by session_id"""
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
        
        filtered = ChatMessage.objects.filter(session_id='session_a')
        assert filtered.count() == 1
        assert filtered.first().id == msg1.id
    
    def test_queryset_filter_by_message_type(self, project):
        """Test filtering messages by type"""
        user_msg = ChatMessage.objects.create(
            project=project,
            message_type='user',
            content='User query'
        )
        asst_msg = ChatMessage.objects.create(
            project=project,
            message_type='assistant',
            content='Assistant response'
        )
        
        user_msgs = ChatMessage.objects.filter(message_type='user')
        assert user_msgs.count() == 1
        assert user_msgs.first().id == user_msg.id
    
    def test_message_user_optional(self, project):
        """Test user field is optional"""
        message = ChatMessage.objects.create(
            project=project,
            message_type='user',
            content='Anonymous query'
        )
        
        assert message.user is None
    
    def test_cascade_delete_project(self, project, authenticated_user):
        """Test messages deleted when project deleted"""
        message = ChatMessage.objects.create(
            project=project,
            user=authenticated_user,
            message_type='user',
            content='Test'
        )
        
        msg_id = message.id
        project.delete()
        
        assert not ChatMessage.objects.filter(id=msg_id).exists()
    
    def test_user_set_to_null_on_deletion(self, project, authenticated_user):
        """Test user set to NULL when user deleted"""
        message = ChatMessage.objects.create(
            project=project,
            user=authenticated_user,
            message_type='user',
            content='Test'
        )
        
        authenticated_user.delete()
        message.refresh_from_db()
        
        assert message.user is None
    
    def test_valid_message_types(self, project):
        """Test valid message type choices"""
        for msg_type, _ in ChatMessage.MESSAGE_TYPES:
            message = ChatMessage.objects.create(
                project=project,
                message_type=msg_type,
                content='Test'
            )
            assert message.message_type == msg_type
    
    def test_project_related_access(self, project, authenticated_user):
        """Test accessing messages from project"""
        msg1 = ChatMessage.objects.create(
            project=project,
            user=authenticated_user,
            message_type='user',
            content='Message 1'
        )
        msg2 = ChatMessage.objects.create(
            project=project,
            user=authenticated_user,
            message_type='assistant',
            content='Message 2'
        )
        
        messages = project.chat_messages.all()
        assert messages.count() == 2
        assert msg1 in messages
        assert msg2 in messages
    
    def test_user_related_access(self, project, authenticated_user):
        """Test accessing messages from user"""
        msg = ChatMessage.objects.create(
            project=project,
            user=authenticated_user,
            message_type='user',
            content='User message'
        )
        
        user_messages = authenticated_user.chat_messages.all()
        assert user_messages.count() == 1
        assert user_messages.first().id == msg.id
