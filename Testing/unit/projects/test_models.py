"""
Unit tests for projects app models
Tests Project and SystemPrompt models
"""

import pytest
from django.utils import timezone
from django.db import IntegrityError
from apps.projects.models import Project, SystemPrompt


@pytest.mark.django_db
class TestProjectModel:
    """Test cases for Project model"""
    
    def test_create_project_local(self):
        """Test creating a local project"""
        project = Project.objects.create(
            project_id='local_20250120_143000_test',
            display_name='Test Project Local',
            storage_type='local',
            description='A test project'
        )
        
        assert project.id is not None
        assert project.display_name == 'Test Project Local'
        assert project.storage_type == 'local'
        assert project.is_active is True
        assert project.document_count == 0
    
    def test_create_project_google(self):
        """Test creating a Google File Search project"""
        project = Project.objects.create(
            project_id='google_test_001',
            display_name='Google Project',
            storage_type='google',
            external_store_id='google_store_123'
        )
        
        assert project.storage_type == 'google'
        assert project.external_store_id == 'google_store_123'
    
    def test_project_id_unique(self):
        """Test that project_id is unique"""
        Project.objects.create(
            project_id='unique_test_001',
            display_name='First Project'
        )
        
        with pytest.raises(IntegrityError):
            Project.objects.create(
                project_id='unique_test_001',
                display_name='Duplicate Project'
            )
    
    def test_project_timestamps(self):
        """Test auto-generated timestamps"""
        before_create = timezone.now()
        project = Project.objects.create(
            project_id='timestamp_test',
            display_name='Timestamp Test'
        )
        after_create = timezone.now()
        
        assert before_create <= project.created_at <= after_create
        assert before_create <= project.updated_at <= after_create
    
    def test_project_str_representation(self):
        """Test __str__ method"""
        project = Project.objects.create(
            project_id='str_test',
            display_name='String Test',
            storage_type='local'
        )
        
        assert str(project) == 'String Test (local)'
    
    def test_project_ordering(self):
        """Test projects are ordered by creation date (newest first)"""
        old_project = Project.objects.create(
            project_id='old_001',
            display_name='Old Project'
        )
        
        new_project = Project.objects.create(
            project_id='new_001',
            display_name='New Project'
        )
        
        projects = list(Project.objects.all())
        assert projects[0].id == new_project.id
        assert projects[1].id == old_project.id
    
    def test_project_is_active_default(self):
        """Test is_active defaults to True"""
        project = Project.objects.create(
            project_id='active_test',
            display_name='Active Test'
        )
        
        assert project.is_active is True
    
    def test_project_storage_type_choices(self):
        """Test valid storage types"""
        valid_types = ['local', 'google']
        
        for storage_type in valid_types:
            project = Project.objects.create(
                project_id=f'storage_{storage_type}',
                display_name=f'{storage_type.title()} Project',
                storage_type=storage_type
            )
            assert project.storage_type == storage_type
    
    def test_project_document_count_default(self):
        """Test document_count defaults to 0"""
        project = Project.objects.create(
            project_id='doc_count_test',
            display_name='Document Count Test'
        )
        
        assert project.document_count == 0
    
    def test_project_last_indexed_at_default(self):
        """Test last_indexed_at is None by default"""
        project = Project.objects.create(
            project_id='indexed_test',
            display_name='Indexed Test'
        )
        
        assert project.last_indexed_at is None
    
    def test_project_update(self):
        """Test updating a project"""
        project = Project.objects.create(
            project_id='update_test',
            display_name='Update Test',
            is_active=True
        )
        
        original_created = project.created_at
        
        project.display_name = 'Updated Name'
        project.is_active = False
        project.save()
        
        refreshed = Project.objects.get(pk=project.pk)
        assert refreshed.display_name == 'Updated Name'
        assert refreshed.is_active is False
        assert refreshed.created_at == original_created
        assert refreshed.updated_at > original_created
    
    def test_project_queryset_filter_by_storage_type(self):
        """Test filtering projects by storage type"""
        Project.objects.create(
            project_id='local_filter_1',
            display_name='Local Project',
            storage_type='local'
        )
        Project.objects.create(
            project_id='google_filter_1',
            display_name='Google Project',
            storage_type='google'
        )
        
        local_projects = Project.objects.filter(storage_type='local')
        assert local_projects.count() == 1
        assert local_projects.first().display_name == 'Local Project'
    
    def test_project_queryset_filter_by_active(self):
        """Test filtering projects by active status"""
        Project.objects.create(
            project_id='active_1',
            display_name='Active Project',
            is_active=True
        )
        Project.objects.create(
            project_id='inactive_1',
            display_name='Inactive Project',
            is_active=False
        )
        
        active = Project.objects.filter(is_active=True)
        assert active.count() == 1
        assert active.first().display_name == 'Active Project'


@pytest.mark.django_db
class TestSystemPromptModel:
    """Test cases for SystemPrompt model"""
    
    def test_create_system_prompt(self):
        """Test creating a system prompt"""
        project = Project.objects.create(
            project_id='prompt_test_proj',
            display_name='Prompt Test Project'
        )
        
        prompt = SystemPrompt.objects.create(
            project=project,
            content='You are a helpful assistant.'
        )
        
        assert prompt.project_id == project.id
        assert prompt.content == 'You are a helpful assistant.'
    
    def test_system_prompt_one_to_one_relationship(self):
        """Test SystemPrompt one-to-one relationship with Project"""
        project = Project.objects.create(
            project_id='one_to_one_test',
            display_name='One-to-One Test'
        )
        
        prompt1 = SystemPrompt.objects.create(
            project=project,
            content='First prompt'
        )
        
        # Creating second prompt for same project should raise error
        with pytest.raises(IntegrityError):
            SystemPrompt.objects.create(
                project=project,
                content='Second prompt'
            )
    
    def test_system_prompt_str_representation(self):
        """Test __str__ method of SystemPrompt"""
        project = Project.objects.create(
            project_id='str_prompt_test',
            display_name='String Prompt Test'
        )
        
        prompt = SystemPrompt.objects.create(
            project=project,
            content='Test prompt'
        )
        
        assert str(prompt) == 'Prompt for String Prompt Test'
    
    def test_system_prompt_empty_content(self):
        """Test creating system prompt with empty content"""
        project = Project.objects.create(
            project_id='empty_prompt_test',
            display_name='Empty Prompt Test'
        )
        
        prompt = SystemPrompt.objects.create(
            project=project,
            content=''
        )
        
        assert prompt.content == ''
    
    def test_system_prompt_timestamps(self):
        """Test timestamps on system prompt"""
        project = Project.objects.create(
            project_id='prompt_timestamp_test',
            display_name='Prompt Timestamp Test'
        )
        
        before = timezone.now()
        prompt = SystemPrompt.objects.create(
            project=project,
            content='Timestamp test'
        )
        after = timezone.now()
        
        assert before <= prompt.created_at <= after
        assert before <= prompt.updated_at <= after
    
    def test_system_prompt_cascade_delete(self):
        """Test that deleting project cascades to prompt"""
        project = Project.objects.create(
            project_id='cascade_test',
            display_name='Cascade Test'
        )
        
        prompt = SystemPrompt.objects.create(
            project=project,
            content='Cascade test prompt'
        )
        
        prompt_id = prompt.id
        project.delete()
        
        # Prompt should be deleted too
        assert SystemPrompt.objects.filter(id=prompt_id).count() == 0
    
    def test_system_prompt_update(self):
        """Test updating system prompt"""
        project = Project.objects.create(
            project_id='update_prompt_test',
            display_name='Update Prompt Test'
        )
        
        prompt = SystemPrompt.objects.create(
            project=project,
            content='Original prompt'
        )
        
        original_created = prompt.created_at
        
        prompt.content = 'Updated prompt'
        prompt.save()
        
        refreshed = SystemPrompt.objects.get(pk=prompt.pk)
        assert refreshed.content == 'Updated prompt'
        assert refreshed.created_at == original_created
        assert refreshed.updated_at > original_created
    
    def test_system_prompt_related_access(self):
        """Test accessing related project through prompt"""
        project = Project.objects.create(
            project_id='related_test',
            display_name='Related Test'
        )
        
        prompt = SystemPrompt.objects.create(
            project=project,
            content='Test'
        )
        
        # Access through prompt
        assert prompt.project.display_name == 'Related Test'
        
        # Access through project
        assert project.system_prompt.content == 'Test'
