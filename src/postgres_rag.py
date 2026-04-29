import os
import json
import shutil
import pypdf
from pathlib import Path
import dotenv
dotenv.load_dotenv()

try:
    from txtai.embeddings import Embeddings
    TXTAI_AVAILABLE = True
except ImportError:
    Embeddings = None
    TXTAI_AVAILABLE = False

try:
    from google import genai
    from google.genai import types
    GENAI_AVAILABLE = True
except ImportError:
    genai = None
    types = None
    GENAI_AVAILABLE = False

POSTGRES_RAG_DEPENDENCIES_AVAILABLE = TXTAI_AVAILABLE

# Base directory for persisted per-project ANN indices
INDICES_DIR = Path(__file__).parent.parent / "rag_data" / "indices"


def cleanup_project_artifacts(project_id: str, document_names: list[str]) -> bool:
    """Best-effort cleanup for a Postgres RAG project's persisted artifacts."""
    if TXTAI_AVAILABLE:
        try:
            rag_engine = PostgresRAGEngine(project_id, require_llm=False)
            return rag_engine.delete_project_artifacts(document_names)
        except ImportError:
            pass

    index_path = INDICES_DIR / project_id
    if index_path.is_dir():
        shutil.rmtree(index_path)
    elif index_path.exists():
        index_path.unlink()

    return True

class PostgresRAGEngine:
    def __init__(self, project_id: str, require_llm: bool = True):
        if not TXTAI_AVAILABLE:
            raise ImportError(
                "PostgresRAGEngine requires the optional AI dependencies. "
                "Install them with: pip install -r requirements-ai.txt"
            )

        if require_llm and not GENAI_AVAILABLE:
            raise ImportError(
                "PostgresRAGEngine LLM queries require google-genai. "
                "Install it with: pip install google-genai"
            )

        self.project_id = project_id
        self.index_path = str(INDICES_DIR / project_id)
        
        # Build the postgres connection string from environment variables
        db_name = os.getenv('DB_NAME', '')
        db_user = os.getenv('DB_USER', '')
        db_pass = os.getenv('DB_PASSWORD', '')
        db_host = os.getenv('DB_HOST', '')
        db_port = os.getenv('DB_PORT', '5432')
        
        if all([db_name, db_user, db_pass, db_host]):
            content_url = f"postgresql://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}"
        else:
            raise ValueError(
                "PostgresRAGEngine requires PostgreSQL configuration via DB_NAME, DB_USER, "
                "DB_PASSWORD, and DB_HOST"
            )

        api_key = os.getenv("GOOGLE_API_KEY", "")
        if require_llm and not api_key:
            raise ValueError("PostgresRAGEngine requires GOOGLE_API_KEY to be set")

        # Load persisted ANN index if it exists, otherwise create a fresh one.
        # txtai separates the ANN vector index (saved to disk) from content storage
        # (text kept in postgres). After a server restart the in-memory index would
        # be empty, so we persist it per-project under rag_data/indices/<project_id>.
        self.embeddings = Embeddings({
            "path": "sentence-transformers/nli-mpnet-base-v2",
            "content": content_url
        })
        if os.path.exists(self.index_path):
            print(f"[INIT] Loading existing index for project: {project_id}")
            self.embeddings.load(self.index_path)
        else:
            print(f"[INIT] Creating new index for project: {project_id}")
        
        # Initialize LLM for query answering
        self.llm_client = genai.Client(api_key=api_key) if require_llm else None

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
            
        # txtai format: (id, text, tags) — tags must be a JSON string, not a dict
        tags = json.dumps({"project_id": self.project_id, "document_name": document_name})
        data = [(document_name, text, tags)]

        # upsert adds to existing index; index() would wipe it
        if os.path.exists(self.index_path):
            self.embeddings.upsert(data)
        else:
            self.embeddings.index(data)

        # Persist the ANN index to disk so queries work after a server restart
        INDICES_DIR.mkdir(parents=True, exist_ok=True)
        self.embeddings.save(self.index_path)
        print(f"[INDEX] Saved index to {self.index_path}")
        return True

    def delete_document(self, document_name: str) -> bool:
        """Delete a document from the txtai index and persist the updated ANN index."""
        self.embeddings.delete([document_name])
        self.embeddings.save(self.index_path)
        return True

    def delete_project_artifacts(self, document_names: list[str]) -> bool:
        """Delete project-scoped indexed content and remove the persisted ANN index."""
        if document_names:
            self.embeddings.delete(document_names)

        if os.path.isdir(self.index_path):
            shutil.rmtree(self.index_path)
        elif os.path.exists(self.index_path):
            os.remove(self.index_path)

        return True

    def query(self, query_text: str, top_k: int = 3, system_prompt: str = "") -> dict:
        """Query the txtai index and use LLM to answer"""
        print(f"[QUERY] Searching for: '{query_text}' in project: {self.project_id}")
        try:
            # With a content backend, search() returns dicts:
            # [{'id': ..., 'text': ..., 'score': ..., 'tags': '{"project_id":...}'}, ...]
            results = self.embeddings.search(query_text, limit=top_k * 2)
            print(f"[QUERY] Found {len(results)} total results")
            if results:
                print(f"[QUERY] First result type: {type(results[0])}, keys: {list(results[0].keys()) if isinstance(results[0], dict) else 'N/A'}")

            source_docs = []
            seen_documents = set()
            context_text = ""

            for i, result in enumerate(results):
                if not result:
                    continue

                # result is a dict when content backend is active
                if isinstance(result, dict):
                    doc_id = result.get('id', '')
                    score  = result.get('score', 0)
                    text   = result.get('text', '')
                else:
                    # Fallback: (id, score) tuple
                    doc_id, score, text = result[0], result[1], ''

                print(f"[QUERY] Result {i}: id={doc_id}, score={score:.4f}")

                # No project filter needed — each engine loads its own per-project
                # ANN index, so all results already belong to self.project_id.
                document_name = str(doc_id)
                if document_name not in seen_documents:
                    source_docs.append({"document": document_name})
                    seen_documents.add(document_name)
                context_text += f"\n---\n{text[:1000]}\n"

                if len(source_docs) >= top_k:
                    break

            print(f"[QUERY] Final matching docs: {len(source_docs)}")
        except Exception as e:
            print(f"❌ Search error: {e}")
            import traceback
            traceback.print_exc()
            source_docs = []
            context_text = ""
            
        if not source_docs:
            response_text = "I don't have any indexed documents to answer this question. Please upload documents first."
        else:
            base_prompt = system_prompt if system_prompt else "Based on the following documents, answer this question:"
            prompt = f"{base_prompt}\\n\\nQuestion: {query_text}\\n\\nDocuments:{context_text}"
            response = self.llm_client.models.generate_content(
                model="gemini-2.5-flash-lite",
                contents=prompt,
                config=types.GenerateContentConfig(temperature=0.7),
            )
            response_text = response.text or ""

        return {
            "response": response_text,
            "source_nodes": source_docs
        }
