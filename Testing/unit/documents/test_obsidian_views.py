"""
Unit tests for Obsidian HTMX partial views in src/apps/documents/views.py
"""

import os
import pytest
from django.urls import reverse
from src.apps.projects.models import Project
from src.apps.documents.models import ObsidianSource, ObsidianFile


@pytest.mark.django_db
class TestObsidianViews:

    def test_set_source_type_view(self, client):
        project = Project.objects.create(
            project_id='view_source_type_test',
            display_name='View Source Type Test',
            storage_type='postgres'
        )
        url = reverse('documents:set_source_type', kwargs={'store_id': project.project_id})
        response = client.post(url, {'source_type': 'obsidian'})

        assert response.status_code == 200
        source = ObsidianSource.objects.get(project=project)
        assert source.source_type == 'obsidian'

    def test_obsidian_save_path_view(self, client, mocker, tmp_path):
        mocker.patch('src.apps.documents.services.LlamaIndexIngestionPipeline')
        tmp_dir = str(tmp_path)
        project = Project.objects.create(
            project_id='view_save_path_test',
            display_name='View Save Path Test',
            storage_type='postgres'
        )
        url = reverse('documents:obsidian_save_path', kwargs={'store_id': project.project_id})
        response = client.post(url, {'vault_path': tmp_dir})

        assert response.status_code == 200
        source = ObsidianSource.objects.get(project=project)
        assert source.vault_path == tmp_dir
        assert b"Vault path saved" in response.content

    def test_obsidian_index_and_sync_views(self, client, mocker, tmp_path):
        mocker.patch('src.apps.documents.services.LlamaIndexIngestionPipeline')
        tmp_dir = str(tmp_path)
        project = Project.objects.create(
            project_id='view_actions_test',
            display_name='View Actions Test',
            storage_type='postgres'
        )
        source = ObsidianSource.objects.create(
            project=project,
            source_type='obsidian',
            vault_path=tmp_dir
        )

        # Test index view
        index_url = reverse('documents:obsidian_index', kwargs={'store_id': project.project_id})
        resp_index = client.post(index_url)
        assert resp_index.status_code == 200
        assert b"Indexed" in resp_index.content

        # Test discover view (formerly sync view)
        sync_url = reverse('documents:obsidian_sync', kwargs={'store_id': project.project_id})
        resp_sync = client.post(sync_url)
        assert resp_sync.status_code == 200
        assert b"Discovered" in resp_sync.content

        # Test hx-confirm presence on Index ALL button when files are indexed
        assert b"hx-confirm=" in resp_index.content or b"Index ALL Obsidian files" in resp_index.content

        # Test index-new view
        new_url = reverse('documents:obsidian_index_new', kwargs={'store_id': project.project_id})
        resp_new = client.post(new_url)
        assert resp_new.status_code == 200
        assert b"Indexed" in resp_new.content

        # Test status GET view
        status_url = reverse('documents:obsidian_status', kwargs={'store_id': project.project_id})
        resp_status = client.get(status_url)
        assert resp_status.status_code == 200
        assert b"Pending" in resp_status.content

    def test_obsidian_status_view_shows_indexed_files(self, client):
        project = Project.objects.create(
            project_id='view_indexed_test',
            display_name='View Indexed Test',
            storage_type='postgres'
        )
        source = ObsidianSource.objects.create(
            project=project,
            source_type='obsidian',
            vault_path='/tmp/vault'
        )
        ObsidianFile.objects.create(
            obsidian_source=source,
            relative_path='Guides/Architecture.md',
            folder_name='Guides',
            status='INDEXED'
        )
        status_url = reverse('documents:obsidian_status', kwargs={'store_id': project.project_id})
        response = client.get(status_url)

        assert response.status_code == 200
        assert b"Indexed Obsidian Notes" in response.content
        assert b"Guides/Architecture.md" in response.content
        assert b"INDEXED" in response.content

    def test_list_documents_renders_upload_form(self, client):
        project = Project.objects.create(
            project_id='view_upload_test',
            display_name='View Upload Test',
            storage_type='postgres'
        )
        url = reverse('documents:list', kwargs={'store_id': project.project_id})
        response = client.get(url)
        assert response.status_code == 200
        assert f'hx-post="/rag/documents/{project.project_id}/upload/"'.encode() in response.content
        assert b'hx-encoding="multipart/form-data"' in response.content
        assert b'type="file"' in response.content
