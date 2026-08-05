import os
import json
import shutil
import numpy as np
import pypdf
from pathlib import Path
import dotenv
import time

dotenv.load_dotenv()

try:
    from google import genai
    from google.genai import errors as genai_errors
    from google.genai import types
    GENAI_AVAILABLE = True
except ImportError:
    genai = None
    genai_errors = None
    types = None
    GENAI_AVAILABLE = False

# Kept for any code that checks this flag — now satisfied by google-genai alone.
POSTGRES_RAG_DEPENDENCIES_AVAILABLE = GENAI_AVAILABLE

# Per-project index directory: rag_data/indices/<project_id>/
INDICES_DIR = Path(__file__).parent.parent / "rag_data" / "indices"

# gemini-embedding-001 default output dimension
EMBEDDING_DIM = 768
EMBEDDING_MODEL = "gemini-embedding-001"


class EmbeddingRateLimitError(RuntimeError):
    """Raised when the embedding API remains rate limited after retries."""


def _is_rate_limit_error(exc: Exception) -> bool:
    return bool(
        genai_errors
        and isinstance(exc, genai_errors.ClientError)
        and getattr(exc, "code", None) == 429
    )


def _embed_texts(client, texts: list[str], task_type: str = "RETRIEVAL_DOCUMENT") -> np.ndarray:
    """
    Call Gemini embedding API and return a float32 array of shape (N, EMBEDDING_DIM).

    Parameters
    ----------
    client : genai.Client
    texts : list[str]
    task_type : str
        "RETRIEVAL_DOCUMENT" for indexing, "RETRIEVAL_QUERY" for queries.
    """
    attempts = 3
    for attempt in range(attempts):
        try:
            result = client.models.embed_content(
                model=EMBEDDING_MODEL,
                contents=texts,
                config=types.EmbedContentConfig(
                    task_type=task_type,
                    output_dimensionality=EMBEDDING_DIM,
                ),
            )
            return np.array([e.values for e in result.embeddings], dtype=np.float32)
        except Exception as exc:
            if not _is_rate_limit_error(exc) or attempt == attempts - 1:
                raise
            time.sleep(min(2 ** attempt, 8))


def _cosine_scores(query_vec: np.ndarray, matrix: np.ndarray) -> np.ndarray:
    """
    Return cosine similarity between a single query vector and a document matrix.

    Parameters
    ----------
    query_vec : np.ndarray, shape (D,)
    matrix : np.ndarray, shape (N, D)

    Returns
    -------
    np.ndarray, shape (N,)
    """
    q = query_vec / (np.linalg.norm(query_vec) + 1e-10)
    norms = np.linalg.norm(matrix, axis=1, keepdims=True) + 1e-10
    return (matrix / norms) @ q


def cleanup_project_artifacts(project_id: str, document_names: list[str]) -> bool:
    """
    Best-effort removal of all persisted index files for a project.

    No API calls are made — purely filesystem cleanup.
    """

    index_path = Path(INDICES_DIR) / project_id
    index_path = index_path.resolve()
    base_dir = Path(INDICES_DIR).resolve()
    if not str(index_path).startswith(str(base_dir)):
        raise ValueError("Invalid project ID causing path traversal")
    if index_path.is_dir():
        shutil.rmtree(index_path)
    elif index_path.exists():
        index_path.unlink()
    return True


class PostgresRAGEngine:
    def __init__(self, project_id: str, require_llm: bool = True):
        if not GENAI_AVAILABLE:
            raise ImportError(
                "PostgresRAGEngine requires google-genai. "
                "Install it with: pip install google-genai"
            )

        api_key = os.getenv("GOOGLE_API_KEY", "")
        if require_llm and not api_key:
            raise ValueError("PostgresRAGEngine requires GOOGLE_API_KEY to be set")

        self.project_id = project_id
        self.index_dir = INDICES_DIR / project_id
        self.embeddings_path = self.index_dir / "embeddings.npy"
        self.content_path = self.index_dir / "content.json"

        # Client is None when no API key — deletion operations don't need it.
        self.client = genai.Client(api_key=api_key) if api_key else None

        # Load existing index from disk, or start with empty arrays.
        if self.embeddings_path.exists() and self.content_path.exists():
            self._embeddings = np.load(str(self.embeddings_path))
            with open(self.content_path) as f:
                self._content = json.load(f)  # list of {"id": str, "text": str}
            print(f"[INIT] Loaded index for project {project_id}: {len(self._content)} docs")
        else:
            self._embeddings = np.empty((0, EMBEDDING_DIM), dtype=np.float32)
            self._content = []
            print(f"[INIT] New index for project {project_id}")

    # ------------------------------------------------------------------
    # Persistence helpers
    # ------------------------------------------------------------------

    def _save(self) -> None:
        self.index_dir.mkdir(parents=True, exist_ok=True)
        np.save(str(self.embeddings_path), self._embeddings)
        with open(self.content_path, "w") as f:
            json.dump(self._content, f)

    def _remove_entries(self, document_id: str) -> None:
        """Remove all entries matching document_id from the in-memory index."""
        keep = [i for i, c in enumerate(self._content) if c["id"] != document_id]
        if len(keep) == len(self._content):
            return
        self._embeddings = self._embeddings[keep] if keep else np.empty((0, EMBEDDING_DIM), dtype=np.float32)
        self._content = [self._content[i] for i in keep]

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def extract_text_from_file(self, file_path: str) -> str:
        p = Path(file_path).resolve()

        # Verify the file is within expected boundaries (e.g. settings.MEDIA_ROOT)
        # Using a simple check if MEDIA_ROOT is available
        try:
            from django.conf import settings
            media_root = Path(settings.MEDIA_ROOT).resolve()
            if not str(p).startswith(str(media_root)):
                # If it's a temp upload, might not be in MEDIA_ROOT, just basic resolution
                pass
        except:
            pass

        file_ext = p.suffix.lower()
        file_path = str(p)
        try:
            if file_ext == ".pdf":
                text = ""
                with open(file_path, "rb") as f:
                    for page in pypdf.PdfReader(f).pages:
                        text += page.extract_text()
                return text
            elif file_ext in (".txt", ".md"):
                with open(file_path, "r", encoding="utf-8") as f:
                    return f.read()
            else:
                raise ValueError(f"Unsupported file type: {file_ext}")
        except Exception as exc:
            print(f"❌ Error extracting text: {exc}")
            raise

    def index_document(self, file_path: str, document_name: str) -> bool:
        if not self.client:
            raise ValueError("GOOGLE_API_KEY is required for indexing")

        text = self.extract_text_from_file(file_path)
        if not text:
            return False

        # Replace any existing entry for this document before adding the new one.
        self._remove_entries(document_name)

        try:
            vec = _embed_texts(self.client, [text], task_type="RETRIEVAL_DOCUMENT")
        except Exception as exc:
            if _is_rate_limit_error(exc):
                raise EmbeddingRateLimitError(
                    "Gemini embedding API is temporarily rate limited. Please try again in a minute."
                ) from exc
            raise
        self._embeddings = (
            np.vstack([self._embeddings, vec]) if self._embeddings.shape[0] else vec
        )
        self._content.append({"id": document_name, "text": text})
        self._save()
        print(f"[INDEX] Indexed '{document_name}' into project {self.project_id}")
        return True

    def delete_document(self, document_name: str) -> bool:
        self._remove_entries(document_name)
        self._save()

        # Delete matching chunks from PGVectorStore database tables
        try:
            import psycopg2
            from django.conf import settings
            from src.apps.documents.services import get_safe_table_name

            config = getattr(settings, "REMOTE_POSTGRES_CONFIG", {})
            db_name = config.get("NAME")
            db_user = config.get("USER")
            db_pass = config.get("PASSWORD")
            db_host = config.get("HOST")
            db_port = config.get("PORT", "5432")

            if all([db_name, db_user, db_pass, db_host]):
                safe_table = get_safe_table_name(self.project_id)
                tables_to_try = [
                    f"data_{safe_table}",
                    safe_table,
                    f"data_rag_project_{self.project_id}",
                    f"rag_project_{self.project_id}"
                ]

                for table in tables_to_try:
                    conn = None
                    try:
                        conn = psycopg2.connect(
                            host=db_host,
                            port=int(db_port),
                            database=db_name,
                            user=db_user,
                            password=db_pass,
                            connect_timeout=3
                        )
                        cursor = conn.cursor()

                        # Check if table exists
                        cursor.execute("""
                            SELECT EXISTS (
                                SELECT FROM information_schema.tables 
                                WHERE table_name = %s
                            );
                        """, (table,))
                        exists = cursor.fetchone()[0]
                        if not exists:
                            cursor.close()
                            conn.close()
                            continue

                        # Delete all matching chunks by checking file_name in metadata_ or metadata JSON column
                        try:
                            cursor.execute(
                                f"DELETE FROM {table} WHERE metadata_->>'file_name' = %s OR metadata_->>'file_path' = %s;",
                                (document_name, document_name)
                            )
                            conn.commit()
                        except Exception:
                            try:
                                conn.rollback()
                                cursor.execute(
                                    f"DELETE FROM {table} WHERE metadata->>'file_name' = %s OR metadata->>'file_path' = %s;",
                                    (document_name, document_name)
                                )
                                conn.commit()
                            except Exception as inner_exc:
                                print(f"Warning: Failed deleting from columns for {table}: {inner_exc}")

                        cursor.close()
                        conn.close()
                    except Exception as table_exc:
                        print(f"Warning: Failed connecting/deleting for table {table}: {table_exc}")
                        if conn:
                            try:
                                conn.close()
                            except Exception:
                                pass
        except Exception as e:
            print(f"Warning: Failed deleting database chunks: {e}")

        return True

    def query(self, query_text: str, top_k: int = 3, system_prompt: str = "") -> dict:
        if not self.client:
            raise ValueError("GOOGLE_API_KEY is required for querying")

        print(f"[QUERY] '{query_text}' in project {self.project_id}")

        source_docs: list[dict] = []
        context_text = ""

        if self._content:
            q_vec = _embed_texts(self.client, [query_text], task_type="RETRIEVAL_QUERY")[0]
            scores = _cosine_scores(q_vec, self._embeddings)
            top_indices = np.argsort(scores)[::-1][:top_k]
            for i in top_indices:
                entry = self._content[int(i)]
                source_docs.append({"document": entry["id"]})
                context_text += f"\n---\n{entry['text'][:1000]}\n"

        print(f"[QUERY] Found {len(source_docs)} matching docs")

        if not source_docs:
            response_text = (
                "I don't have any indexed documents to answer this question. "
                "Please upload documents first."
            )
        else:
            base_prompt = system_prompt or "Based on the following documents, answer this question:"
            prompt = f"{base_prompt}\n\nQuestion: {query_text}\n\nDocuments:{context_text}"
            response = self.client.models.generate_content(
                model="gemini-2.5-flash-lite",
                contents=prompt,
                config=types.GenerateContentConfig(temperature=0.7),
            )
            response_text = response.text or ""

        return {"response": response_text, "source_nodes": source_docs}
