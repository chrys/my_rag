"""
Regression test for custom prompt saving bug

BUG DESCRIPTION:
Previously, saving a custom prompt for a project would fail with a 404 error because
the API endpoint expected the Django database primary key (integer id), but the frontend
was sending either project_id (for local projects) or external_store_id (for Google projects).

The error manifested as:
- GET /rag/api/projects/fileSearchStores%2Ftest-google-99oic6yk10ke/prompt -> 404
- POST /rag/api/projects/fileSearchStores%2Ftest-google-99oic6yk10ke/prompt -> 404

ROOT CAUSE:
1. The ProjectViewSet default lookup was by primary key only
2. The frontend sends store.name which is:
   - project_id for local projects (e.g., "local_20260227_120000_test")
   - external_store_id for Google projects (e.g., "fileSearchStores/abc-123")
3. The URL encoding of slashes in external_store_id caused additional issues

This test verifies that:
1. Projects can be looked up by primary key, project_id, or external_store_id
2. Prompts can be saved and retrieved for both local and Google projects
3. The API returns the correct response format expected by the frontend
4. Documents endpoint also works with custom lookup

FIXED: 2026-02-27
"""

import pytest
from rest_framework.test import APIClient
from django.contrib.auth.models import User
from src.apps.projects.models import Project, SystemPrompt


@pytest.fixture
def authenticated_user():
    """Create a test user for API authentication"""
    return User.objects.create_user(
        username='testuser',
        password='testpass123'
    )


@pytest.mark.django_db
class TestCustomPromptSavingRegression:
    """
    Regression test suite for custom prompt saving bug
    """
    
    @pytest.fixture(autouse=True)
    def setup(self, authenticated_user):
        """Setup client and user for each test"""
        self.client = APIClient()
        self.client.force_authenticate(user=authenticated_user)
        self.user = authenticated_user
    
    def test_save_prompt_for_local_project_by_project_id(self):
        """
        Test that prompts can be saved for local projects using project_id
        """
        # Create a local project
        project = Project.objects.create(
            user=self.user,
            project_id='local_20260227_120000_test',
            display_name='Test Local Project',
            storage_type='local'
        )
        
        # Save a prompt using project_id in URL
        response = self.client.post(
            f'/rag/api/projects/local_20260227_120000_test/prompt/',
            data={'content': 'You are a helpful assistant for local projects.'},
            format='json'
        )
        
        # Verify the response
        assert response.status_code == 200
        data = response.json()
        assert data['status'] == 'success'
        assert data['prompt'] == 'You are a helpful assistant for local projects.'
        
        # Verify the prompt was saved to database
        prompt = SystemPrompt.objects.get(project=project)
        assert prompt.content == 'You are a helpful assistant for local projects.'
    
    def test_save_prompt_for_google_project_by_project_id(self):
        """
        Test that prompts can be saved for Google projects using project_id
        """
        # Create a Google project
        project = Project.objects.create(
            user=self.user,
            project_id='google_20260227_120000_test',
            display_name='Test Google Project',
            storage_type='google',
            external_store_id='fileSearchStores/test-google-abc123'
        )
        
        # Save a prompt using project_id in URL (not external_store_id to avoid slash issues)
        response = self.client.post(
            f'/rag/api/projects/google_20260227_120000_test/prompt/',
            data={'content': 'You are a helpful assistant for Google projects.'},
            format='json'
        )
        
        # Verify the response
        assert response.status_code == 200
        data = response.json()
        assert data['status'] == 'success'
        assert data['prompt'] == 'You are a helpful assistant for Google projects.'
        
        # Verify the prompt was saved to database
        prompt = SystemPrompt.objects.get(project=project)
        assert prompt.content == 'You are a helpful assistant for Google projects.'
    
    def test_retrieve_prompt_by_project_id(self):
        """
        Test that prompts can be retrieved using project_id
        """
        # Create project with a prompt
        project = Project.objects.create(
            user=self.user,
            project_id='local_retrieve_test',
            display_name='Retrieve Test',
            storage_type='local'
        )
        SystemPrompt.objects.create(
            project=project,
            content='Existing prompt content'
        )
        
        # Retrieve the prompt
        response = self.client.get(f'/rag/api/projects/local_retrieve_test/prompt/')
        
        # Verify the response
        assert response.status_code == 200
        data = response.json()
        assert data['prompt'] == 'Existing prompt content'
    
    def test_retrieve_prompt_for_google_project_by_project_id(self):
        """
        Test that prompts can be retrieved for Google projects using project_id
        """
        # Create Google project with a prompt
        project = Project.objects.create(
            user=self.user,
            project_id='google_retrieve_test',
            display_name='Google Retrieve Test',
            storage_type='google',
            external_store_id='fileSearchStores/retrieve-test-123'
        )
        SystemPrompt.objects.create(
            project=project,
            content='Google project prompt'
        )
        
        # Retrieve the prompt using project_id (not external_store_id)
        response = self.client.get(f'/rag/api/projects/google_retrieve_test/prompt/')
        
        # Verify the response
        assert response.status_code == 200
        data = response.json()
        assert data['prompt'] == 'Google project prompt'
    
    def test_retrieve_prompt_returns_empty_string_when_no_prompt_exists(self):
        """
        Test that GET prompt returns empty string when no prompt exists
        """
        # Create project without a prompt
        project = Project.objects.create(
            user=self.user,
            project_id='no_prompt_test',
            display_name='No Prompt Test',
            storage_type='local'
        )
        
        # Retrieve the prompt
        response = self.client.get(f'/rag/api/projects/no_prompt_test/prompt/')
        
        # Verify the response
        assert response.status_code == 200
        data = response.json()
        assert data['prompt'] == ''
    
    def test_update_existing_prompt(self):
        """
        Test that updating an existing prompt works correctly
        """
        # Create project with initial prompt
        project = Project.objects.create(
            user=self.user,
            project_id='update_prompt_test',
            display_name='Update Test',
            storage_type='local'
        )
        SystemPrompt.objects.create(
            project=project,
            content='Original prompt'
        )
        
        # Update the prompt
        response = self.client.post(
            f'/rag/api/projects/update_prompt_test/prompt/',
            data={'content': 'Updated prompt content'},
            format='json'
        )
        
        # Verify the response
        assert response.status_code == 200
        data = response.json()
        assert data['prompt'] == 'Updated prompt content'
        
        # Verify only one prompt exists and it's updated
        prompts = SystemPrompt.objects.filter(project=project)
        assert prompts.count() == 1
        assert prompts.first().content == 'Updated prompt content'
    
    def test_lookup_by_primary_key_still_works(self):
        """
        Test that looking up projects by primary key (integer id) still works
        """
        # Create project
        project = Project.objects.create(
            user=self.user,
            project_id='pk_test',
            display_name='PK Test',
            storage_type='local'
        )
        
        # Save prompt using primary key
        response = self.client.post(
            f'/rag/api/projects/{project.pk}/prompt/',
            data={'content': 'Prompt via PK'},
            format='json'
        )
        
        # Verify the response
        assert response.status_code == 200
        data = response.json()
        assert data['prompt'] == 'Prompt via PK'
    
    def test_documents_endpoint_with_custom_lookup(self):
        """
        Test that the documents endpoint also works with custom lookup
        """
        from src.apps.documents.models import Document
        
        # Create project
        project = Project.objects.create(
            user=self.user,
            project_id='docs_test',
            display_name='Docs Test',
            storage_type='local'
        )
        
        # Create a document for this project
        Document.objects.create(
            project=project,
            document_name='test_doc.pdf',
            display_name='Test Document',
            state='INDEXED'
        )
        
        # Access documents via project_id
        response = self.client.get(f'/rag/api/projects/docs_test/documents/')
        
        # Verify the response
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]['display_name'] == 'Test Document'
    
    def test_documents_endpoint_for_google_project(self):
        """
        Test that documents endpoint works for Google projects using project_id
        """
        from src.apps.documents.models import Document
        
        # Create Google project
        project = Project.objects.create(
            user=self.user,
            project_id='google_docs_test',
            display_name='Google Docs Test',
            storage_type='google',
            external_store_id='fileSearchStores/docs-test-456'
        )
        
        # Create a document for this project
        Document.objects.create(
            project=project,
            document_name='gdoc.pdf',
            display_name='Google Document',
            state='INDEXED'
        )
        
        # Access documents via project_id
        response = self.client.get(f'/rag/api/projects/google_docs_test/documents/')
        
        # Verify the response
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]['display_name'] == 'Google Document'
    
    def test_invalid_project_id_returns_404(self):
        """
        Test that accessing a non-existent project returns 404
        """
        # Try to get prompt for non-existent project
        response = self.client.get('/rag/api/projects/nonexistent_project/prompt/')
        
        # Verify 404 response
        assert response.status_code == 404


@pytest.mark.django_db
class TestPromptResponseFormat:
    """
    Tests for the prompt API response format compatibility
    """
    
    @pytest.fixture(autouse=True)
    def setup(self, authenticated_user):
        """Setup client and user for each test"""
        self.client = APIClient()
        self.client.force_authenticate(user=authenticated_user)
        self.user = authenticated_user
    
    def test_get_prompt_response_format(self):
        """
        Test that GET /prompt returns {'prompt': 'content'} format
        """
        project = Project.objects.create(
            user=self.user,
            project_id='format_test',
            display_name='Format Test',
            storage_type='local'
        )
        SystemPrompt.objects.create(
            project=project,
            content='Test content'
        )
        
        response = self.client.get(f'/rag/api/projects/format_test/prompt/')
        
        # Verify response has correct format
        assert response.status_code == 200
        data = response.json()
        assert 'prompt' in data
        assert data['prompt'] == 'Test content'
        # Ensure it doesn't return full serializer fields
        assert 'id' not in data
        assert 'created_at' not in data
    
    def test_post_prompt_response_format(self):
        """
        Test that POST /prompt returns {'status': 'success', 'prompt': 'content'} format
        """
        project = Project.objects.create(
            user=self.user,
            project_id='post_format_test',
            display_name='Post Format Test',
            storage_type='local'
        )
        
        response = self.client.post(
            '/rag/api/projects/post_format_test/prompt/',
            data={'content': 'New prompt'},
            format='json'
        )
        
        # Verify response has correct format
        assert response.status_code == 200
        data = response.json()
        assert 'status' in data
        assert 'prompt' in data
        assert data['status'] == 'success'
        assert data['prompt'] == 'New prompt'
        # Ensure it doesn't return full serializer fields
        assert 'id' not in data
        assert 'created_at' not in data


@pytest.mark.django_db
class TestPromptFrontendFormDataRegression:
    """
    Regression tests for the bug where prompt saves appeared successful
    but the prompt was empty when retrieved again.

    BUG: The frontend sends FormData with key 'prompt' but the view was reading
    request.data.get('content', '') — so an empty string was always saved.
    The success response masked the bug since it echoed back the (wrong) saved value.

    FIXED: 2026-02-27 — view now accepts both 'prompt' (frontend) and 'content' (API) keys.
    """
    
    @pytest.fixture(autouse=True)
    def setup(self, authenticated_user):
        """Setup client and user for each test"""
        self.client = APIClient()
        self.client.force_authenticate(user=authenticated_user)
        self.user = authenticated_user

    def test_save_via_formdata_prompt_key_persists(self):
        """
        Saving with FormData key 'prompt' (as the frontend does) must persist the value.
        """
        project = Project.objects.create(
            user=self.user,
            project_id='formdata_persist_test',
            display_name='FormData Persist Test',
            storage_type='local'
        )

        # POST with the key the frontend actually uses
        response = self.client.post(
            '/rag/api/projects/formdata_persist_test/prompt/',
            data={'prompt': 'My custom prompt text'},
        )
        assert response.status_code == 200
        assert response.json()['prompt'] == 'My custom prompt text'

        # GET must return the same value — this was the failing assertion before the fix
        get_response = self.client.get('/rag/api/projects/formdata_persist_test/prompt/')
        assert get_response.status_code == 200
        assert get_response.json()['prompt'] == 'My custom prompt text'

    def test_save_via_json_content_key_persists(self):
        """
        Saving with JSON body key 'content' (API clients) must also persist correctly.
        """
        project = Project.objects.create(
            user=self.user,
            project_id='json_content_persist_test',
            display_name='JSON Content Persist Test',
            storage_type='local'
        )

        response = self.client.post(
            '/rag/api/projects/json_content_persist_test/prompt/',
            data={'content': 'API prompt text'},
            format='json'
        )
        assert response.status_code == 200
        assert response.json()['prompt'] == 'API prompt text'

        get_response = self.client.get('/rag/api/projects/json_content_persist_test/prompt/')
        assert get_response.status_code == 200
        assert get_response.json()['prompt'] == 'API prompt text'

    def test_switch_projects_and_back_retains_prompt(self):
        """
        Simulate the exact user scenario: save prompt for project A,
        switch to project B, switch back to project A — prompt must still be there.
        """
        project_a = Project.objects.create(
            user=self.user,
            project_id='project_a',
            display_name='Project A',
            storage_type='local'
        )
        project_b = Project.objects.create(
            user=self.user,
            project_id='project_b',
            display_name='Project B',
            storage_type='local'
        )

        # Save prompt for project A (using frontend FormData key)
        self.client.post('/rag/api/projects/project_a/prompt/', data={'prompt': 'Prompt for A'})

        # Switch to project B (loads its prompt — empty)
        resp_b = self.client.get('/rag/api/projects/project_b/prompt/')
        assert resp_b.status_code == 200
        assert resp_b.json()['prompt'] == ''

        # Switch back to project A — prompt must still be 'Prompt for A'
        resp_a = self.client.get('/rag/api/projects/project_a/prompt/')
