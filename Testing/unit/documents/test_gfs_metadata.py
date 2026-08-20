"""
Unit tests for 3-Step Metadata Extraction Pipeline & GFS Formatter (Task 4)
"""

import os
import pytest
from unittest.mock import MagicMock, patch
from src.apps.documents.services import (
    extract_system_and_file_metadata,
    extract_ai_metadata_with_gemini_flash,
    format_and_validate_gfs_metadata,
)


class TestGFSMetadataPipeline:
    """Test system metadata extraction, AI pre-extraction, and GFS typing/truncation"""

    def test_extract_system_and_file_metadata(self, tmp_path):
        """Test extraction of deterministic system properties"""
        test_file = tmp_path / "budget_report.txt"
        test_file.write_text("Company budget report 2026")

        mock_user = MagicMock()
        mock_user.username = "chrys"

        meta = extract_system_and_file_metadata(str(test_file), "budget_report.txt", user=mock_user)
        meta_dict = {item["key"]: item.get("string_value") if "string_value" in item else item.get("numeric_value") for item in meta}

        assert meta_dict["file_name"] == "budget_report.txt"
        assert meta_dict["file_type"] == ".txt"
        assert meta_dict["uploader"] == "chrys"
        assert "file_size_kb" in meta_dict
        assert "created_date" in meta_dict

    @patch("src.google_file_search.client")
    def test_extract_ai_metadata_success(self, mock_client):
        """Test Gemini Flash AI classification into structured metadata"""
        mock_response = MagicMock()
        mock_response.text = '{"document_type": "Invoice", "department": "Finance", "language": "en"}'
        mock_client.models.generate_content.return_value = mock_response

        meta = extract_ai_metadata_with_gemini_flash("Invoice #123 for consulting services.")
        meta_dict = {item["key"]: item.get("string_value") if "string_value" in item else item.get("numeric_value") for item in meta}

        assert meta_dict.get("document_type") == "Invoice"
        assert meta_dict.get("department") == "Finance"
        assert meta_dict.get("language") == "en"

    @patch("src.google_file_search.client")
    def test_extract_ai_metadata_fallback_on_error(self, mock_client):
        """Test graceful fallback returning empty list when AI call fails"""
        mock_client.models.generate_content.side_effect = RuntimeError("API rate limited")

        meta = extract_ai_metadata_with_gemini_flash("Some document text")
        assert meta == []

    def test_format_and_validate_gfs_metadata_rules(self):
        """Test GFS metadata rules: max 20 entries, mutually exclusive string/numeric values, key sanitization"""
        raw_metadata = [
            {"key": "valid_str", "value": "text_val"},
            {"key": "valid_num", "value": 42},
            {"key": "float_num", "value": "123.45"},
            {"key": "invalid-key name!", "value": "sanitized"},
        ]
        # Add 25 extra keys to verify 20-cap truncation
        for i in range(25):
            raw_metadata.append({"key": f"extra_key_{i}", "value": f"val_{i}"})

        formatted = format_and_validate_gfs_metadata(raw_metadata)

        # Enforce max 20 items
        assert len(formatted) == 20

        # Enforce typing and exclusivity
        for item in formatted:
            assert "key" in item
            assert ("string_value" in item) ^ ("numeric_value" in item)

        # Verify key sanitization (letters, numbers, underscore)
        keys = [item["key"] for item in formatted]
        assert "invalid_key_name" in keys or "invalidkeyname" in keys
