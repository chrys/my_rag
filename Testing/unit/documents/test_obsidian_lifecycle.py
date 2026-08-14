"""
Unit tests for Obsidian 3-stage lifecycle engine in src/apps/documents/services.py
"""

import os
import pytest
from src.apps.projects.models import Project
from src.apps.documents.models import ObsidianSource, ObsidianFile
from src.apps.documents.services import (
    discover_obsidian_vault_files,
    run_obsidian_lifecycle,
)


@pytest.mark.django_db
class TestObsidianLifecycleEngine:

    def test_discover_obsidian_vault_files_sync_and_purge(self, tmp_path):
        tmp_dir = str(tmp_path)
        # Create files on disk
        file1 = os.path.join(tmp_dir, "Note1.md")
        file2 = os.path.join(tmp_dir, "Note2.md")
        with open(file1, "w") as f:
            f.write("Content 1")
        with open(file2, "w") as f:
            f.write("Content 2")

        project = Project.objects.create(
            project_id='lifecycle_test_proj',
            display_name='Lifecycle Test Project',
            storage_type='postgres'
        )
        source = ObsidianSource.objects.create(
            project=project,
            source_type='obsidian',
            vault_path=tmp_dir
        )

        # Discover stage
        db_files = discover_obsidian_vault_files(source)
        assert len(db_files) == 2
        assert ObsidianFile.objects.filter(obsidian_source=source).count() == 2

        # Remove file1 from disk and re-discover
        os.remove(file1)
        db_files_after_delete = discover_obsidian_vault_files(source)
        assert len(db_files_after_delete) == 1
        assert ObsidianFile.objects.filter(obsidian_source=source).count() == 1
        assert ObsidianFile.objects.filter(obsidian_source=source).first().relative_path == "Note2.md"

    def test_run_obsidian_lifecycle_modes(self, mocker, tmp_path):
        mocker.patch('src.apps.documents.services.LlamaIndexIngestionPipeline')
        tmp_dir = str(tmp_path / "vault1")
        os.makedirs(tmp_dir, exist_ok=True)

        file1 = os.path.join(tmp_dir, "Guide1.md")
        file2 = os.path.join(tmp_dir, "Guide2.md")
        with open(file1, "w") as f:
            f.write("# Guide 1\nSee [[Guide2]]")
        with open(file2, "w") as f:
            f.write("# Guide 2\nDetails")

        project = Project.objects.create(
            project_id='lifecycle_modes_proj',
            display_name='Lifecycle Modes Project',
            storage_type='postgres'
        )
        source = ObsidianSource.objects.create(
            project=project,
            source_type='obsidian',
            vault_path=tmp_dir
        )

        # Full mode indexing
        result_full = run_obsidian_lifecycle(source, mode='full')
        assert result_full['total_files'] == 2
        assert result_full['indexed_count'] == 2
        assert project.reload().document_count == 2 if hasattr(project, 'reload') else Project.objects.get(pk=project.pk).document_count == 2

        # Discover mode test (should populate files as PENDING without indexing)
        discover_dir = str(tmp_path / "vault_disc")
        os.makedirs(discover_dir, exist_ok=True)
        file_disc = os.path.join(discover_dir, "DiscNote.md")
        with open(file_disc, "w") as f:
            f.write("# Discover Test")
        source_disc = ObsidianSource.objects.create(
            project=Project.objects.create(project_id='disc_proj', storage_type='postgres'),
            source_type='obsidian',
            vault_path=discover_dir
        )
        res_disc = run_obsidian_lifecycle(source_disc, mode='discover')
        assert res_disc['total_files'] == 1
        assert res_disc['indexed_count'] == 0
        f_obj = ObsidianFile.objects.get(obsidian_source=source_disc, relative_path="DiscNote.md")
        assert f_obj.status == 'PENDING'
