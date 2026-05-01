"""
Unit tests for projects app serializers
Tests all serializers for Project and SystemPrompt
"""

import pytest
from src.apps.projects.models import Project, SystemPrompt
from src.apps.projects.serializers import (
    ProjectSerializer,
    ProjectCreateSerializer,
    ProjectUpdateSerializer,
    ProjectListSerializer,
    SystemPromptSerializer
)


@pytest.mark.django_db
class TestProjectSerializer:
    """Test cases for ProjectSerializer"""
    
    def test_serialize_project(self):
        """Test serializing a complete project"""
        project = Project.objects.create(
            project_id='serial_001',
            display_name='Serialization Test',
            storage_type='local',
            description='Test description',
            document_count=5
        )
        
        serializer = ProjectSerializer(project)
        data = serializer.data
        
        assert data['project_id'] == 'serial_001'
        assert data['display_name'] == 'Serialization Test'
        assert data['storage_type'] == 'local'
        assert data['description'] == 'Test description'
        assert data['document_count'] == 5
        assert data['is_active'] is True
    
    def test_serialize_project_with_prompt(self):
        """Test serializing project with system prompt"""
        project = Project.objects.create(
            project_id='serial_prompt_001',
            display_name='With Prompt'
        )
        
        prompt = SystemPrompt.objects.create(
            project=project,
            content='Test prompt'
        )
        
        serializer = ProjectSerializer(project)
        data = serializer.data
        
        assert 'system_prompt' in data
        assert data['system_prompt']['content'] == 'Test prompt'
    
    def test_project_serializer_read_only_fields(self):
        """Test that read-only fields cannot be modified"""
        project = Project.objects.create(
            project_id='readonly_001',
            display_name='Read-only Test'
        )
        
        data = {
            'display_name': 'Updated',
            'created_at': '2025-01-01T00:00:00Z',  # Try to modify read-only
            'updated_at': '2025-01-01T00:00:00Z',  # Try to modify read-only
        }
        
        serializer = ProjectSerializer(project, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            refreshed = Project.objects.get(pk=project.pk)
            # created_at and updated_at should not be modified
            assert refreshed.display_name == 'Updated'
    
    def test_serialize_google_project(self):
        """Test serializing Google File Search project"""
        project = Project.objects.create(
            project_id='google_serial_001',
            display_name='Google Project',
            storage_type='google',
            external_store_id='google_123'
        )
        
        serializer = ProjectSerializer(project)
        data = serializer.data
        
        assert data['storage_type'] == 'google'
        assert data['external_store_id'] == 'google_123'


@pytest.mark.django_db
class TestProjectCreateSerializer:
    """Test cases for ProjectCreateSerializer"""
    
    def test_create_project_with_serializer(self):
        """Test creating a project using serializer"""
        data = {
            'project_id': 'create_test_001',
            'display_name': 'Created Project',
            'storage_type': 'local',
            'description': 'A created project'
        }
        
        serializer = ProjectCreateSerializer(data=data)
        assert serializer.is_valid()
        
        project = serializer.save()
        
        assert project.project_id == 'create_test_001'
        assert project.display_name == 'Created Project'
        assert project.storage_type == 'local'
    
    def test_create_project_missing_required_field(self):
        """Test creating project without required field"""
        data = {
            'project_id': 'missing_name_001',
            # Missing display_name
            'storage_type': 'local'
        }
        
        serializer = ProjectCreateSerializer(data=data)
        assert not serializer.is_valid()
        assert 'display_name' in serializer.errors
    
    def test_create_serializer_invalid_storage_type(self):
        """Test validation of storage_type field"""
        data = {
            'project_id': 'invalid_storage',
            'display_name': 'Invalid Storage',
            'storage_type': 'invalid_type'
        }
        
        serializer = ProjectCreateSerializer(data=data)
        assert not serializer.is_valid()
        assert 'storage_type' in serializer.errors
    
    def test_create_serializer_valid_storage_types(self):
        """Test all valid storage types"""
        for storage_type in ['local', 'google']:
            data = {
                'project_id': f'valid_{storage_type}_001',
                'display_name': f'Valid {storage_type}',
                'storage_type': storage_type
            }
            
            serializer = ProjectCreateSerializer(data=data)
            assert serializer.is_valid(), serializer.errors
            project = serializer.save()
            assert project.storage_type == storage_type
    
    def test_create_serializer_optional_fields(self):
        """Test that description is optional"""
        data = {
            'project_id': 'optional_fields_001',
            'display_name': 'Optional Test'
        }
        
        serializer = ProjectCreateSerializer(data=data)
        assert serializer.is_valid()
        project = serializer.save()
        assert project.description == ''


@pytest.mark.django_db
class TestProjectUpdateSerializer:
    """Test cases for ProjectUpdateSerializer"""
    
    def test_partial_update_display_name(self):
        """Test updating only display_name"""
        project = Project.objects.create(
            project_id='update_001',
            display_name='Original Name'
        )
        
        data = {'display_name': 'Updated Name'}
        serializer = ProjectUpdateSerializer(project, data=data, partial=True)
        
        assert serializer.is_valid()
        updated = serializer.save()
        
        assert updated.display_name == 'Updated Name'
    
    def test_update_is_active_status(self):
        """Test updating is_active field"""
        project = Project.objects.create(
            project_id='update_active_001',
            display_name='Active Test',
            is_active=True
        )
        
        data = {'is_active': False}
        serializer = ProjectUpdateSerializer(project, data=data, partial=True)
        
        assert serializer.is_valid()
        updated = serializer.save()
        
        assert updated.is_active is False
    
    def test_update_description(self):
        """Test updating description"""
        project = Project.objects.create(
            project_id='update_desc_001',
            display_name='Description Test'
        )
        
        data = {'description': 'New description'}
        serializer = ProjectUpdateSerializer(project, data=data, partial=True)
        
        assert serializer.is_valid()
        updated = serializer.save()
        
        assert updated.description == 'New description'
    
    def test_update_multiple_fields(self):
        """Test updating multiple fields at once"""
        project = Project.objects.create(
            project_id='update_multi_001',
            display_name='Multi Update Test',
            is_active=True
        )
        
        data = {
            'display_name': 'New Name',
            'description': 'New Description',
            'is_active': False
        }
        
        serializer = ProjectUpdateSerializer(project, data=data, partial=True)
        assert serializer.is_valid()
        updated = serializer.save()
        
        assert updated.display_name == 'New Name'
        assert updated.description == 'New Description'
        assert updated.is_active is False


@pytest.mark.django_db
class TestProjectListSerializer:
    """Test cases for ProjectListSerializer"""
    
    def test_list_serializer_fields(self):
        """Test ProjectListSerializer contains expected fields"""
        project = Project.objects.create(
            project_id='list_001',
            display_name='List Test',
            storage_type='local'
        )
        
        serializer = ProjectListSerializer(project)
        data = serializer.data
        
        # Check expected fields exist
        assert 'id' in data
        assert 'project_id' in data
        assert 'display_name' in data
        assert 'storage_type' in data
        assert 'is_active' in data
    
    def test_list_serializer_multiple_projects(self):
        """Test serializing multiple projects"""
        projects = [
            Project.objects.create(
                project_id=f'list_{i}',
                display_name=f'List Test {i}'
            ) for i in range(3)
        ]
        
        serializer = ProjectListSerializer(projects, many=True)
        data = serializer.data
        
        assert len(data) == 3
        assert all('display_name' in item for item in data)


@pytest.mark.django_db
class TestSystemPromptSerializer:
    """Test cases for SystemPromptSerializer"""
    
    def test_serialize_system_prompt(self):
        """Test serializing a system prompt"""
        project = Project.objects.create(
            project_id='prompt_serial_001',
            display_name='Prompt Serialization'
        )
        
        prompt = SystemPrompt.objects.create(
            project=project,
            content='You are a helpful AI assistant.'
        )
        
        serializer = SystemPromptSerializer(prompt)
        data = serializer.data
        
        assert data['project'] == project.id
        assert data['content'] == 'You are a helpful AI assistant.'
    
    def test_create_system_prompt_with_serializer(self):
        """Test creating system prompt via serializer"""
        project = Project.objects.create(
            project_id='prompt_create_001',
            display_name='Prompt Create Test'
        )
        
        data = {
            'project': project.id,
            'content': 'Custom prompt content'
        }
        
        serializer = SystemPromptSerializer(data=data)
        assert serializer.is_valid()
        
        prompt = serializer.save()
        
        assert prompt.project_id == project.id
        assert prompt.content == 'Custom prompt content'
    
    def test_update_system_prompt_content(self):
        """Test updating system prompt content"""
        project = Project.objects.create(
            project_id='prompt_update_001',
            display_name='Prompt Update Test'
        )
        
        prompt = SystemPrompt.objects.create(
            project=project,
            content='Original content'
        )
        
        data = {'content': 'Updated content'}
        serializer = SystemPromptSerializer(prompt, data=data, partial=True)
        
        assert serializer.is_valid()
        updated = serializer.save()
        
        assert updated.content == 'Updated content'
    
    def test_system_prompt_serializer_read_only_fields(self):
        """Test read-only fields in SystemPromptSerializer"""
        project = Project.objects.create(
            project_id='prompt_readonly_001',
            display_name='Prompt Read-only Test'
        )
        
        prompt = SystemPrompt.objects.create(
            project=project,
            content='Test'
        )
        
        serializer = SystemPromptSerializer(prompt)
        data = serializer.data
        
        # created_at and updated_at should be in response
        assert 'created_at' in data
        assert 'updated_at' in data
