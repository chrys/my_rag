import pytest
from unittest.mock import MagicMock, patch
from src.apps.documents.services import LlamaIndexIngestionPipeline
from src.apps.documents.models import Document
from src.apps.projects.models import Project
import pytest
from unittest.mock import MagicMock, patch
from src.apps.documents.services import LlamaIndexIngestionPipeline
from src.apps.projects.models import Project

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
        MockEmbedding.assert_called_with(model_name="models/embedding-001", api_key=ANY)
