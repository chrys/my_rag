"""
Unit tests for Document Format & Ingestion Hygiene Gate (Task 3)
"""

import os
import pytest
from src.apps.documents.services import (
    compute_file_sha256,
    check_document_hygiene,
    strip_noisy_artifacts,
)


class TestDocumentHygiene:
    """Test format validation, size checks, SHA-256 calculation, and artifact stripping"""

    def test_compute_file_sha256(self, tmp_path):
        """Test SHA-256 computation on a binary/text file"""
        test_file = tmp_path / "sample.txt"
        test_file.write_text("Hello World RAG")
        hash_val = compute_file_sha256(str(test_file))
        assert len(hash_val) == 64
        # SHA-256 of "Hello World RAG"
        import hashlib
        expected = hashlib.sha256(b"Hello World RAG").hexdigest()
        assert hash_val == expected

    def test_check_document_hygiene_valid_txt(self, tmp_path):
        """Test hygiene check succeeds on a valid small text file"""
        test_file = tmp_path / "doc.txt"
        test_file.write_text("Valid text content")
        result = check_document_hygiene(str(test_file), "doc.txt")
        assert result["valid"] is True
        assert result["error"] is None
        assert result["file_size"] > 0
        assert result["content_hash"] is not None

    def test_check_document_hygiene_zero_bytes(self, tmp_path):
        """Test hygiene check rejects 0-byte empty files"""
        empty_file = tmp_path / "empty.txt"
        empty_file.write_text("")
        result = check_document_hygiene(str(empty_file), "empty.txt")
        assert result["valid"] is False
        assert "empty" in result["error"].lower() or "0 byte" in result["error"].lower()

    def test_check_document_hygiene_exceeds_100mb(self, tmp_path, monkeypatch):
        """Test hygiene check rejects files larger than 100MB"""
        test_file = tmp_path / "huge.pdf"
        test_file.write_text("fake huge content")

        # Mock os.path.getsize to return 105 MB
        monkeypatch.setattr("os.path.getsize", lambda p: 105 * 1024 * 1024)
        result = check_document_hygiene(str(test_file), "huge.pdf")
        assert result["valid"] is False
        assert "100 mb" in result["error"].lower() or "limit" in result["error"].lower()

    def test_check_document_hygiene_unsupported_format(self, tmp_path):
        """Test hygiene check rejects unsupported file extension (e.g. .exe)"""
        exe_file = tmp_path / "app.exe"
        exe_file.write_bytes(b"MZ\x90\x00")
        result = check_document_hygiene(str(exe_file), "app.exe")
        assert result["valid"] is False
        assert "unsupported" in result["error"].lower() or "format" in result["error"].lower()

    def test_strip_noisy_artifacts_pagination_and_boilerplate(self):
        """Test stripping page numbers, headers, footers, and repeated whitespace"""
        raw_text = (
            "Company confidential header\n"
            "Page 1 of 10\n\n"
            "This is the actual important document body.\n"
            "- 1 -\n"
            "42\n"
            "All rights reserved. Copyright 2026.\n\n\n\n"
            "Next paragraph with meaningful insights.\n"
        )
        cleaned = strip_noisy_artifacts(raw_text)
        assert "Page 1 of 10" not in cleaned
        assert "- 1 -" not in cleaned
        assert "This is the actual important document body." in cleaned
        assert "Next paragraph with meaningful insights." in cleaned
        assert "\n\n\n\n" not in cleaned
