import pytest
from unittest.mock import patch, MagicMock, mock_open
from src.postgres_rag import PostgresRAGEngine

@pytest.fixture
def mock_env_vars(monkeypatch):
    monkeypatch.setenv('DB_NAME', 'test_db')
    monkeypatch.setenv('DB_USER', 'test_user')
    monkeypatch.setenv('DB_PASSWORD', 'test_pass')
    monkeypatch.setenv('DB_HOST', 'localhost')
    monkeypatch.setenv('DB_PORT', '5432')

class TestPostgresRAGEngine:
    def test_initialization(self, mock_env_vars):
        """Test that the engine initializes with txtai embeddings"""
        engine = PostgresRAGEngine(project_id="test_proj_123")
        assert engine.project_id == "test_proj_123"
        assert hasattr(engine, 'embeddings')
        
    def test_initialization_fallback(self, monkeypatch):
        """Test initialization fallback to sqlite when env vars are missing"""
        monkeypatch.setenv('DB_NAME', '')
        engine = PostgresRAGEngine(project_id="test_proj_123")
        assert hasattr(engine, 'embeddings')

    def test_extract_text_txt(self, mock_env_vars):
        """Test extracting text from txt file"""
        engine = PostgresRAGEngine(project_id="test_proj_123")
        with patch('builtins.open', mock_open(read_data="text content")):
            text = engine.extract_text_from_file("test.txt")
        assert text == "text content"
        
    @patch('src.postgres_rag.pypdf.PdfReader')
    def test_extract_text_pdf(self, mock_pdf_reader, mock_env_vars):
        """Test extracting text from pdf file"""
        mock_page = MagicMock()
        mock_page.extract_text.return_value = "pdf content "
        mock_pdf_reader.return_value.pages = [mock_page, mock_page]
        
        engine = PostgresRAGEngine(project_id="test_proj_123")
        with patch('builtins.open', mock_open()):
            text = engine.extract_text_from_file("test.pdf")
            
        assert text == "pdf content pdf content "

    def test_extract_text_unsupported(self, mock_env_vars):
        """Test extracting text from unsupported file"""
        engine = PostgresRAGEngine(project_id="test_proj_123")
        with pytest.raises(Exception):
            engine.extract_text_from_file("test.jpg")

    @patch('src.postgres_rag.PostgresRAGEngine.extract_text_from_file')
    def test_index_document(self, mock_extract, mock_env_vars):
        """Test indexing a document into postgres using txtai"""
        mock_extract.return_value = "This is a test document content."
        engine = PostgresRAGEngine(project_id="test_proj_123")
        engine.embeddings = MagicMock()
        
        result = engine.index_document(file_path="test.txt", document_name="test_doc")
        
        assert result is True
        mock_extract.assert_called_once_with("test.txt")
        engine.embeddings.index.assert_called_once()
        
    @patch('src.postgres_rag.PostgresRAGEngine.extract_text_from_file')
    def test_index_document_empty(self, mock_extract, mock_env_vars):
        """Test indexing an empty document"""
        mock_extract.return_value = ""
        engine = PostgresRAGEngine(project_id="test_proj_123")
        engine.embeddings = MagicMock()
        
        result = engine.index_document(file_path="test.txt", document_name="test_doc")
        
        assert result is False
        engine.embeddings.index.assert_not_called()

    def test_query(self, mock_env_vars):
        """Test querying the indexed documents"""
        engine = PostgresRAGEngine(project_id="test_proj_123")
        
        # Test with dict result
        engine.embeddings = MagicMock()
        engine.embeddings.search.return_value = [{"id": "0", "text": "This is a test document content.", "score": 0.99}]
        engine.llm = MagicMock()
        engine.llm.complete.return_value.text = "This is the generated answer."
        
        response = engine.query("What is this?")
        
        assert response["response"] == "This is the generated answer."
        assert len(response["source_nodes"]) == 1
        
    def test_query_tuple_result(self, mock_env_vars):
        """Test querying when txtai returns tuples"""
        engine = PostgresRAGEngine(project_id="test_proj_123")
        
        # Test with tuple result (id, text, score)
        engine.embeddings = MagicMock()
        engine.embeddings.search.return_value = [("0", "Test content", 0.95)]
        engine.llm = MagicMock()
        engine.llm.complete.return_value.text = "Tuple answer."
        
        response = engine.query("Question?")
        
        assert response["response"] == "Tuple answer."
        assert response["source_nodes"][0]["document"] == "0"
        
    def test_query_empty(self, mock_env_vars):
        """Test querying with no results"""
        engine = PostgresRAGEngine(project_id="test_proj_123")
        engine.embeddings = MagicMock()
        engine.embeddings.search.return_value = []
        
        response = engine.query("What is this?")
        
        assert "I don't have any indexed documents" in response["response"]
