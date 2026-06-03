import os
os.environ["GOOGLE_API_KEY"] = "AIzaSyDummyKeyForTesting"

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


@pytest.mark.django_db
class TestSyntheticQAEvaluator:
    """Unit tests for the restored SyntheticQAEvaluator service class"""

    @pytest.fixture
    def project(self):
        """Create a test project"""
        return Project.objects.create(
            project_id="test_proj_evaluator",
            display_name="Evaluator Project"
        )

    @patch("src.apps.evaluate.eval_services.genai.Client")
    def test_evaluator_initialization(self, mock_client, project):
        """Test SyntheticQAEvaluator can be initialized and configures settings"""
        from src.apps.evaluate.eval_services import SyntheticQAEvaluator
        evaluator = SyntheticQAEvaluator(project.project_id)
        assert evaluator.project_id == project.project_id
        assert evaluator.embed_model is not None

    @patch("src.apps.evaluate.eval_services.genai.Client")
    @patch("psycopg2.connect")
    @patch("src.apps.evaluate.eval_services.settings")
    def test_fetch_document_nodes(self, mock_settings, mock_connect, mock_client, project):
        """Test fetch_document_nodes retrieves nodes from database using psycopg2"""
        from src.apps.evaluate.eval_services import SyntheticQAEvaluator
        mock_settings.REMOTE_POSTGRES_CONFIG = {
            "NAME": "db",
            "USER": "user",
            "PASSWORD": "pwd",
            "HOST": "host",
            "PORT": "5432"
        }

        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.fetchall.return_value = [
            ("id1", "Text chunk 1", "node_id_1", '{"file_name": "test.pdf"}')
        ]

        evaluator = SyntheticQAEvaluator(project.project_id)
        nodes = evaluator.fetch_document_nodes("test.pdf")

        assert len(nodes) == 1
        assert nodes[0]["node_id"] == "node_id_1"
        assert nodes[0]["text"] == "Text chunk 1"

    @patch("src.apps.evaluate.eval_services.genai.Client")
    def test_generate_synthetic_questions(self, mock_client_class, project):
        """Test generate_synthetic_questions queries Gemini model and parses results"""
        from src.apps.evaluate.eval_services import SyntheticQAEvaluator
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        
        # Mock API generate_content response
        mock_response = MagicMock()
        mock_response.text = "Question 1?\nQuestion 2?\nQuestion 3?"
        mock_client.models.generate_content.return_value = mock_response

        evaluator = SyntheticQAEvaluator(project.project_id)
        questions = evaluator.generate_synthetic_questions("Some text content")

        assert len(questions) == 3
        assert questions[0] == "Question 1?"
        assert questions[1] == "Question 2?"
        assert questions[2] == "Question 3?"

    @patch("src.apps.evaluate.eval_services.get_vector_store")
    @patch("src.apps.evaluate.eval_services.VectorStoreIndex")
    @patch("src.apps.evaluate.eval_services.genai.Client")
    def test_evaluate_retrieval_recall(self, mock_client_class, mock_index_class, mock_get_store, project):
        """Test evaluate_retrieval_recall flow and scoring"""
        from src.apps.evaluate.eval_services import SyntheticQAEvaluator
        
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        mock_response = MagicMock()
        mock_response.text = "Q1?\nQ2?\nQ3?"
        mock_client.models.generate_content.return_value = mock_response

        # Mock vector index and retriever
        mock_node = MagicMock()
        mock_node.node.node_id = "node_id_1"
        mock_retriever = MagicMock()
        mock_retriever.retrieve.return_value = [mock_node]
        mock_index = MagicMock()
        mock_index.as_retriever.return_value = mock_retriever
        mock_index_class.from_vector_store.return_value = mock_index

        evaluator = SyntheticQAEvaluator(project.project_id)
        
        # Stub fetch_document_nodes to return 1 node
        evaluator.fetch_document_nodes = MagicMock(return_value=[
            {"id": "id1", "text": "Text chunk 1", "node_id": "node_id_1", "metadata": {}}
        ])

        results = evaluator.evaluate_retrieval_recall("test.pdf")

        assert results["recall_score"] == 100.0
        assert results["total_questions"] == 3
        assert results["matches"] == 3
        assert len(results["logs"]) == 3
        assert results["logs"][0]["success"] is True


@pytest.mark.django_db
class TestRunEvaluationView:
    """Unit tests for the restored RunEvaluationView custom admin view"""

    @pytest.fixture
    def setup_user_and_project(self):
        """Create a user and project for view tests"""
        user = User.objects.create_user(username="testadmin", password="password")
        project = Project.objects.create(
            project_id="postgres_test_proj",
            display_name="Postgres Project",
        )
        # Create a document record
        from src.apps.documents.models import Document
        document = Document.objects.create(
            project=project,
            document_name="test_doc.pdf",
            display_name="Test Document",
            state="INDEXED"
        )
        return user, project, document

    @patch("src.apps.evaluate.eval_services.genai.Client")
    @patch("src.apps.evaluate.eval_services.SyntheticQAEvaluator.evaluate_retrieval_recall")
    def test_run_evaluation_view_post_success(self, mock_eval_recall, mock_client, setup_user_and_project):
        """Test successful POST to RunEvaluationView triggering Synthetic QA"""
        user, project, document = setup_user_and_project
        
        mock_eval_recall.return_value = {
            "recall_score": 100.0,
            "total_questions": 3,
            "matches": 3,
            "logs": [
                {"question": "Q1?", "expected_node_id": "n1", "success": True, "citations": ["n1"]}
            ]
        }

        from django.test import Client
        client = Client()
        client.force_login(user)

        from django.urls import reverse
        url = reverse("custom_admin:run-evaluation")
        
        response = client.post(url, {
            "project_id": project.project_id,
            "document_id": document.id,
            "eval_method": "synthetic_qa"
        })

        assert response.status_code == 200
        # Verify scorecard and log rendering in the HTML response
        content = response.content.decode("utf-8")
        assert "Retrieval Recall" in content
        assert "100.0%" in content
        assert "Test Questions" in content
        assert "Citations Matched" in content



