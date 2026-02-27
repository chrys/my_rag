import os
from txtai.embeddings import Embeddings
import pypdf
from pathlib import Path
from llama_index.llms.ollama import Ollama

class PostgresRAGEngine:
    def __init__(self, project_id: str):
        self.project_id = project_id
        
        # Build the postgres connection string from environment variables
        db_name = os.getenv('DB_NAME', '')
        db_user = os.getenv('DB_USER', '')
        db_pass = os.getenv('DB_PASSWORD', '')
        db_host = os.getenv('DB_HOST', '')
        db_port = os.getenv('DB_PORT', '5432')
        
        # Use a local SQLite fallback if postgres env vars are not set (for testing/safety)
        if all([db_name, db_user, db_pass, db_host]):
            content_url = f"postgresql://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}"
        else:
            content_url = "sqlite:///txtai_fallback.db"
            print("⚠️ Postgres environment variables not fully set. Falling back to SQLite.")

        # Initialize txtai Embeddings with the postgres backend
        self.embeddings = Embeddings({
            "path": "sentence-transformers/nli-mpnet-base-v2", 
            "content": content_url
        })
        
        # Initialize LLM for query answering
        self.llm = Ollama(
            model="gemma3:4b",
            base_url="http://localhost:11434",
            temperature=0.7
        )

    def extract_text_from_file(self, file_path: str) -> str:
        """Extract text from various file formats"""
        file_ext = Path(file_path).suffix.lower()
        try:
            if file_ext == '.pdf':
                text = ""
                with open(file_path, 'rb') as file:
                    pdf_reader = pypdf.PdfReader(file)
                    for page in pdf_reader.pages:
                        text += page.extract_text()
                return text
            elif file_ext in ['.txt', '.md']:
                with open(file_path, 'r', encoding='utf-8') as f:
                    return f.read()
            else:
                raise ValueError(f"Unsupported file type: {file_ext}")
        except Exception as e:
            print(f"❌ Error extracting text: {e}")
            raise

    def index_document(self, file_path: str, document_name: str) -> bool:
        """Extract text and index it using txtai"""
        text = self.extract_text_from_file(file_path)
        if not text:
            return False
            
        # We store project_id and document_name as metadata
        data = [(file_path, {"text": text, "project_id": self.project_id, "document_name": document_name}, None)]
        self.embeddings.index(data)
        return True

    def query(self, query_text: str, top_k: int = 3, system_prompt: str = "") -> dict:
        """Query the txtai index and use LLM to answer"""
        # Filter by this project's ID
        search_query = f"select id, text, score from txtai where similar('{query_text}') and project_id = '{self.project_id}' limit {top_k}"
        results = self.embeddings.search(search_query)
        
        source_docs = []
        context_text = ""
        
        for result in results:
            # Result format depends on if it's a dict or tuple
            if isinstance(result, dict):
                score = result.get('score', 0)
                text = result.get('text', '')
                doc_id = result.get('id', 'Unknown')
            else:
                # If tuple, assuming (id, text, score) based on the select statement
                doc_id = result[0] if len(result) > 0 else 'Unknown'
                text = result[1] if len(result) > 1 else ''
                score = result[2] if len(result) > 2 else 0
                
            source_docs.append({
                "document": str(doc_id),
                "score": float(score)
            })
            context_text += f"\n---\n{text[:1000]}\n"
            
        if not source_docs:
            response_text = "I don't have any indexed documents to answer this question. Please upload documents first."
        else:
            base_prompt = system_prompt if system_prompt else "Based on the following documents, answer this question:"
            prompt = f"{base_prompt}\\n\\nQuestion: {query_text}\\n\\nDocuments:{context_text}"
            response_text = self.llm.complete(prompt).text if hasattr(self.llm, 'complete') else str(self.llm(prompt))

        return {
            "response": response_text,
            "source_nodes": source_docs
        }
