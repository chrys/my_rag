import pytest
import uuid
from unittest.mock import patch, MagicMock
from django.contrib.auth.models import User
from src.apps.evaluate.models import EvaluationDataset, EvaluationRun, EvaluationResultMetrics
from src.apps.evaluate.eval_services import (
    generate_synthetic_qas,
    execute_evaluation_run,
    QA_GEN_STATUS,
)
from src.apps.projects.models import Project


@pytest.mark.django_db
class TestEvaluationServices:
    """Unit tests for RAG evaluation and QA synthesis services"""

    @pytest.fixture
    def project(self):
        """Create a test project"""
        return Project.objects.create(
            project_id="test_proj_services",
            display_name="Services Project"
        )

    @patch("src.apps.evaluate.eval_services._get_postgres_chunks")
    @patch("src.apps.evaluate.eval_services.GoogleGenAI")
    def test_generate_synthetic_qas_success(self, mock_llm_class, mock_get_chunks, project):
        """Test successful generation of synthetic QAs using mocked Gemini LLM"""
        # Mock text chunks
        mock_get_chunks.return_value = [
            {"text": "Chunk 1 content", "metadata": {"file_name": "doc1.pdf"}},
            {"text": "Chunk 2 content", "metadata": {"file_name": "doc2.pdf"}}
        ]

        # Mock LLM response returning JSON QA pairs
        mock_llm = MagicMock()
        mock_response = MagicMock()
        mock_response.text = '[{"question": "Q1?", "ground_truth": "A1."}, {"question": "Q2?", "ground_truth": "A2."}]'
        mock_llm.complete.return_value = mock_response
        mock_llm_class.return_value = mock_llm

        # Run generator
        generate_synthetic_qas(project.project_id, num_questions=2)

        # Check status dictionary
        assert QA_GEN_STATUS[project.project_id]["status"] == "SUCCESS"
        assert QA_GEN_STATUS[project.project_id]["count"] == 2

        # Check database rows created
        qas = EvaluationDataset.objects.filter(project=project)
        assert qas.count() == 2
        assert qas[0].question in ["Q1?", "Q2?"]
        assert qas[0].ground_truth in ["A1.", "A2."]
        assert qas[0].source == "GENERATED"

    @patch("src.apps.evaluate.eval_services.get_vector_store")
    @patch("src.apps.evaluate.eval_services.VectorStoreIndex")
    @patch("src.apps.evaluate.eval_services.GoogleGenAI")
    @patch("src.apps.evaluate.eval_services.GeminiEmbedding")
    def test_execute_evaluation_run_success(self, mock_embed, mock_llm_class, mock_index_class, mock_get_store, project):
        """Test full RAG evaluation run and scoring under mock environment"""
        # Create validation items in DB
        EvaluationDataset.objects.create(
            project=project,
            question="Q?",
            ground_truth="A.",
            source="MANUAL"
        )

        run = EvaluationRun.objects.create(
            project=project,
            status="PENDING"
        )

        # Mock LlamaIndex retriever returning mock nodes
        mock_node = MagicMock()
        mock_node.text = "Mock context text chunk retrieved"
        mock_retriever = MagicMock()
        mock_retriever.retrieve.return_value = [mock_node]
        
        mock_index = MagicMock()
        mock_index.as_retriever.return_value = mock_retriever
        mock_index_class.from_vector_store.return_value = mock_index

        # Mock Gemini LLM responses for both QA synthesis and metrics scoring
        mock_llm = MagicMock()
        mock_response = MagicMock()
        mock_response.text = "0.9"  # Metric score fallback return
        mock_llm.complete.return_value = mock_response
        mock_llm_class.return_value = mock_llm

        # Run evaluation service
        execute_evaluation_run(run.id)

        # Refresh from database and check run status
        run.refresh_from_db()
        assert run.status == "SUCCESS"
        assert run.completed_at is not None

        # Check metrics generated
        metrics = EvaluationResultMetrics.objects.filter(run=run)
        assert metrics.count() == 1
        assert metrics[0].context_recall == 0.9
        assert metrics[0].context_precision == 0.9
        assert metrics[0].faithfulness == 0.9
        assert metrics[0].answer_relevancy == 0.9

    @patch("src.apps.evaluate.eval_services.settings")
    @patch("psycopg2.connect")
    def test_get_postgres_chunks_fallback(self, mock_connect, mock_settings):
        """Test _get_postgres_chunks queries metadata_ first, and falls back to metadata on exception"""
        from src.apps.evaluate.eval_services import _get_postgres_chunks

        # Mock settings credentials to pass early check
        mock_settings.REMOTE_POSTGRES_CONFIG = {
            "NAME": "test_db",
            "USER": "user",
            "PASSWORD": "pwd",
            "HOST": "host",
            "PORT": "5432"
        }

        # Mock psycopg2 connection, cursor, fetchone
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        # First return True for exists check
        mock_cursor.fetchone.side_effect = [
            (True,),  # exists fetchone for first table
        ]
        mock_cursor.fetchall.return_value = [
            ("Chunk content", '{"file_name": "test.pdf"}')  # fetchall for query
        ]

        # First execute on SELECT text, metadata_ raises column error
        def execute_side_effect(query, *args, **kwargs):
            if "metadata_" in query:
                raise Exception('column "metadata_" does not exist')
            return MagicMock()

        mock_cursor.execute.side_effect = execute_side_effect

        # Run method
        chunks = _get_postgres_chunks("postgres_2026")
        
        # Verify psycopg2 conn rollback is called on failure of metadata_ query
        mock_conn.rollback.assert_called_once()
        # Verify fallback query was made
        any_metadata_query = any("metadata" in call[0][0] and "metadata_" not in call[0][0] for call in mock_cursor.execute.call_args_list)
        assert any_metadata_query
        assert len(chunks) == 1
        assert chunks[0]["text"] == "Chunk content"
        assert chunks[0]["metadata"]["file_name"] == "test.pdf"

