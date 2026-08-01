"""
Unit tests for ObsidianSource and ObsidianFile models in documents app
"""

import pytest
from src.apps.projects.models import Project
from src.apps.documents.models import ObsidianSource, ObsidianFile


@pytest.mark.django_db
class TestObsidianModels:
    """Test cases for ObsidianSource and ObsidianFile models"""

    def test_create_obsidian_source(self):
        project = Project.objects.create(
            project_id='obsidian_model_test',
            display_name='Obsidian Model Test',
            storage_type='postgres'
        )
        source = ObsidianSource.objects.create(
            project=project,
            source_type='obsidian',
            vault_path='/tmp/test_vault'
        )

        assert source.id is not None
        assert source.project == project
        assert source.source_type == 'obsidian'
        assert source.vault_path == '/tmp/test_vault'

    def test_create_obsidian_file(self):
        project = Project.objects.create(
            project_id='obsidian_file_test',
            display_name='Obsidian File Test',
            storage_type='postgres'
        )
        source = ObsidianSource.objects.create(
            project=project,
            source_type='obsidian',
            vault_path='/tmp/test_vault'
        )
        obsidian_file = ObsidianFile.objects.create(
            obsidian_source=source,
            relative_path='Certifications/AWS_Guide.md',
            folder_name='AWS',
            status='PENDING',
            file_mtime=1700000000.0
        )

        assert obsidian_file.id is not None
        assert obsidian_file.relative_path == 'Certifications/AWS_Guide.md'
        assert obsidian_file.folder_name == 'AWS'
        assert obsidian_file.status == 'PENDING'
        assert obsidian_file.file_mtime == 1700000000.0
