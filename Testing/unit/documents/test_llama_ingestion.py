import sys
from unittest.mock import MagicMock, patch

import pytest
from src.apps.documents.services import (
    LlamaIndexIngestionPipeline,
    check_structural_quality,
    get_safe_table_name,
    select_node_parser,
)
from llama_index.core.node_parser import MarkdownNodeParser, SentenceSplitter
from src.apps.projects.models import Project
from src.apps.documents.models import Document


@pytest.mark.django_db
def test_llama_ingestion_pipeline_triggered():
    # Setup: Create a project
    project = Project.objects.create(display_name="RAG Test Project", project_id="test_id", storage_type="postgres")

    with patch("src.apps.documents.services.VectorStoreIndex") as MockIndex, \
         patch("src.apps.documents.services.SimpleDirectoryReader") as MockReader:
        # Mock load_data to avoid file not found
        MockReader.return_value.load_data.return_value = ["mock_doc"]
        pipeline = LlamaIndexIngestionPipeline(project_id="test_id")
        pipeline.index_document(file_path="tests/test_file.txt")

        # Verify index was called
        MockIndex.from_documents.assert_called_once()

@pytest.mark.django_db
def test_embedding_model_instantiation():
    # Verify the gemini-embedding-001 is used
    with patch("src.apps.documents.services.GeminiEmbedding") as MockEmbedding:
        pipeline = LlamaIndexIngestionPipeline(project_id="test_id")

        from unittest.mock import ANY
        # Verify model was instantiated with correct params
        MockEmbedding.assert_called_with(model_name="models/gemini-embedding-001", api_key=ANY)

@pytest.mark.django_db
def test_llama_ingestion_pipeline_original_filename():
    project = Project.objects.create(display_name="RAG Test Project", project_id="test_id", storage_type="postgres")
    
    with patch("src.apps.documents.services.VectorStoreIndex") as MockIndex, \
         patch("src.apps.documents.services.SimpleDirectoryReader") as MockReader:
        
        mock_doc = MagicMock()
        mock_doc.metadata = {}
        MockReader.return_value.load_data.return_value = [mock_doc]
        
        pipeline = LlamaIndexIngestionPipeline(project_id="test_id")
        pipeline.index_document(file_path="tests/test_file.txt", original_filename="my_essay.txt")
        
        assert mock_doc.metadata['file_name'] == "my_essay.txt"
        assert mock_doc.metadata['file_path'] == "my_essay.txt"
        MockIndex.from_documents.assert_called_once()


def test_get_safe_table_name():
    # Test short project_id (should not change)
    name_short = get_safe_table_name("short_id")
    assert name_short == "rag_project_short_id"
    
    # Test extremely long project_id (should be truncated to keep under 48 characters)
    long_id = "a" * 100
    name_long = get_safe_table_name(long_id)
    assert len(name_long) <= 48
    assert name_long.startswith("rag_project_")
    
    # Test uniqueness and determinism
    name_long_2 = get_safe_table_name(long_id)
    assert name_long == name_long_2
    
    name_other = get_safe_table_name("a" * 99 + "b")
    assert name_long != name_other


def test_select_node_parser_autodetect():
    md_parser = select_node_parser("doc.md", strategy="auto_detect")
    assert isinstance(md_parser, MarkdownNodeParser)

    txt_parser = select_node_parser("notes.txt", strategy="auto_detect")
    assert isinstance(txt_parser, SentenceSplitter)


class TestStructuralQualityGrading:
    """Test suite for check_structural_quality quality gate logic"""

    @patch("google.genai.Client")
    @patch("llama_index.core.SimpleDirectoryReader")
    def test_quality_grading_blocks_low_quality(self, mock_reader, mock_genai):
        """Test that a document with a quality score <= 7 raises ValueError"""
        # Mock SimpleDirectoryReader to return garbage essay text
        mock_doc = MagicMock()
        mock_doc.text = "TheCompanyReport2024 CID:12 CID:44 Revenue $5M Introduction to spacingmashups."
        mock_reader.return_value.load_data.return_value = [mock_doc]

        # Mock Gemini client to return a score of 7/10 (quality threshold boundary)
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_parsed = MagicMock()
        mock_parsed.score = 7
        mock_parsed.reason = "Shattered sentences, words mashed together, and raw font codes found."
        mock_response.parsed = mock_parsed
        mock_client.models.generate_content.return_value = mock_response
        mock_genai.return_value = mock_client

        # Run quality check and verify it raises ValueError
        with pytest.raises(ValueError) as excinfo:
            check_structural_quality("garbage-essay.txt")

        assert "Extraction quality too low (Score: 7/10). Reason: Shattered sentences, words mashed together, and raw font codes found." in str(excinfo.value)

    @patch("google.genai.Client")
    @patch("llama_index.core.SimpleDirectoryReader")
    def test_quality_grading_allows_high_quality(self, mock_reader, mock_genai):
        """Test that a document with a quality score > 7 executes successfully without error"""
        mock_doc = MagicMock()
        mock_doc.text = "This is a clean, well-formatted and perfectly readable report."
        mock_reader.return_value.load_data.return_value = [mock_doc]

        # Mock Gemini client to return a score of 8/10 (acceptable)
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_parsed = MagicMock()
        mock_parsed.score = 8
        mock_parsed.reason = "Text is clean and structure is intact."
        mock_response.parsed = mock_parsed
        mock_client.models.generate_content.return_value = mock_response
        mock_genai.return_value = mock_client

        # Run quality check and verify it succeeds without raising any error
        try:
            check_structural_quality("clean-essay.txt")
        except ValueError as exc:
            pytest.fail(f"Quality check raised ValueError unexpectedly: {exc}")


@pytest.mark.django_db
@patch("django.conf.settings")
@patch("psycopg2.connect")
def test_postgres_rag_engine_delete_document_db_cleanup(mock_connect, mock_settings):
    """Test that PostgresRAGEngine delete_document method executes SQL DELETE queries to clean up chunks"""
    from src.postgres_rag import PostgresRAGEngine

    # Mock settings credentials
    mock_settings.REMOTE_POSTGRES_CONFIG = {
        "NAME": "test_db",
        "USER": "user",
        "PASSWORD": "pwd",
        "HOST": "host",
        "PORT": "5432"
    }

    # Mock psycopg2 connection, cursor, exists check fetchone
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_connect.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchone.return_value = (True,)  # exists check returns True

    # Setup the engine and run delete
    engine = PostgresRAGEngine("postgres_proj_test", require_llm=False)
    engine.delete_document("garbage-essay.txt")

    # Verify psycopg2 connection was made
    mock_connect.assert_called()

    # Verify that DELETE query was executed
    delete_queries = [call[0][0] for call in mock_cursor.execute.call_args_list if "DELETE FROM" in call[0][0]]
    assert len(delete_queries) > 0
    assert any("metadata_" in q or "metadata" in q for q in delete_queries)
    
    # Verify commit was called
    mock_conn.commit.assert_called()

