"""
Unit tests for Obsidian scanner, Markdown sanitizer, and metadata enricher in src/apps/documents/services.py
"""

import os
import tempfile
import pytest
from src.apps.documents.services import (
    sanitize_obsidian_markdown,
    scan_obsidian_vault,
    enrich_chunk_metadata,
)


def test_sanitize_obsidian_markdown_links():
    raw_markdown = """
# AWS Overview
Check out [[Certifications/AWS_Guide|AWS Certification Guide]] for details.
Also see [[Cloud Architecture]] notes and [[Architecture/Design|System Design]].
"""
    cleaned = sanitize_obsidian_markdown(raw_markdown)

    assert "[[Certifications/AWS_Guide|AWS Certification Guide]]" not in cleaned
    assert "AWS Certification Guide" in cleaned
    assert "[[Cloud Architecture]]" not in cleaned
    assert "Cloud Architecture" in cleaned
    assert "System Design" in cleaned


def test_scan_obsidian_vault_exclusions():
    with tempfile.TemporaryDirectory() as tmp_dir:
        # Create excluded directory structure
        obsidian_dir = os.path.join(tmp_dir, ".obsidian")
        resources_dir = os.path.join(tmp_dir, "_resources")
        cert_dir = os.path.join(tmp_dir, "Certifications")
        aws_dir = os.path.join(cert_dir, "AWS")

        os.makedirs(obsidian_dir, exist_ok=True)
        os.makedirs(resources_dir, exist_ok=True)
        os.makedirs(aws_dir, exist_ok=True)

        # Create valid and excluded files
        valid_note = os.path.join(aws_dir, "AWS_Guide.md")
        root_note = os.path.join(tmp_dir, "Readme.md")
        obsidian_config = os.path.join(obsidian_dir, "config.json")
        resource_img = os.path.join(resources_dir, "image.png")
        binary_file = os.path.join(aws_dir, "diagram.png")
        canvas_file = os.path.join(aws_dir, "mindmap.canvas")
        untitled_draft = os.path.join(aws_dir, "Untitled 1.md")

        for fpath in [valid_note, root_note, obsidian_config, resource_img, binary_file, canvas_file, untitled_draft]:
            with open(fpath, "w") as f:
                f.write("# Content")

        discovered = scan_obsidian_vault(tmp_dir)
        discovered_rel_paths = [d["relative_path"] for d in discovered]

        assert "Certifications/AWS/AWS_Guide.md" in discovered_rel_paths
        assert "Readme.md" in discovered_rel_paths
        assert len(discovered) == 2

        # Check immediate parent folder name attribution
        aws_entry = next(d for d in discovered if d["relative_path"] == "Certifications/AWS/AWS_Guide.md")
        assert aws_entry["folder_name"] == "AWS"

        root_entry = next(d for d in discovered if d["relative_path"] == "Readme.md")
        assert root_entry["folder_name"] == "Root"


def test_enrich_chunk_metadata():
    initial_meta = {"source": "local"}
    enriched = enrich_chunk_metadata(initial_meta, folder="AWS", file_name="Certifications/AWS_Guide.md", project_id="proj_123")

    assert enriched["folder"] == "AWS"
    assert enriched["file_name"] == "Certifications/AWS_Guide.md"
    assert enriched["project_id"] == "proj_123"
    assert enriched["source"] == "local"
