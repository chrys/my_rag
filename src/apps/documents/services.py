import os
from django.conf import settings
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, StorageContext
from llama_index.vector_stores.postgres import PGVectorStore
from llama_index.embeddings.google import GeminiEmbedding

import logging
logger = logging.getLogger(__name__)

def get_safe_table_name(project_id: str) -> str:
    """
    Return a postgres-safe table name under 48 characters to keep "data_" + table name
    and automatically generated index names (e.g. {table_name}_idx_1) under 63 bytes.
    Uses MD5 hash to ensure uniqueness while preserving a readable prefix.
    """
    base_name = f"rag_project_{project_id}"
    if len(base_name) > 48:
        import hashlib
        hash_suffix = hashlib.md5(project_id.encode('utf-8')).hexdigest()[:8]
        max_id_len = 48 - 12 - 9  # 48 - len("rag_project_") - len("_hash")
        truncated_id = project_id[:max_id_len]
        return f"rag_project_{truncated_id}_{hash_suffix}"
    return base_name

from llama_index.core.node_parser import (
    CodeSplitter,
    HierarchicalNodeParser,
    MarkdownNodeParser,
    SentenceSplitter,
)


def select_node_parser(file_path: str, strategy: str = "auto_detect"):
    """
    Factory function returning the appropriate LlamaIndex NodeParser instance.
    Gracefully falls back to SentenceSplitter if specialized dependencies are missing or fail.
    """
    ext = os.path.splitext(file_path)[1].lower()

    try:
        if strategy == "markdown" or (strategy == "auto_detect" and ext == ".md"):
            return MarkdownNodeParser.from_defaults()

        elif strategy == "code" or (strategy == "auto_detect" and ext in [".py", ".js", ".ts", ".html"]):
            language_map = {
                ".py": "python",
                ".js": "javascript",
                ".ts": "typescript",
                ".html": "html"
            }
            target_lang = language_map.get(ext, "python")
            return CodeSplitter(
                language=target_lang,
                chunk_lines=40,
                chunk_lines_overlap=5,
                max_chars=1500
            )

        elif strategy == "hierarchical":
            return HierarchicalNodeParser.from_defaults(chunk_sizes=[1024, 256])

        else:
            return SentenceSplitter(chunk_size=512, chunk_overlap=50)

    except Exception as exc:
        logger.warning(f"Failed to initialize node parser for {file_path} (strategy: {strategy}): {exc}. Falling back to SentenceSplitter.")
        return SentenceSplitter(chunk_size=512, chunk_overlap=50)


class LlamaIndexIngestionPipeline:
    def __init__(self, project_id):
        self.project_id = project_id
        # Configure gemini-embedding-001
        self.embed_model = GeminiEmbedding(
            model_name="models/gemini-embedding-001",
            api_key=os.getenv("GOOGLE_API_KEY")
        )
        
    def index_document(self, file_path, original_filename: str = None, strategy: str = "auto_detect"):
        # Read the document
        documents = SimpleDirectoryReader(input_files=[file_path]).load_data()
        
        if original_filename:
            for doc in documents:
                doc.metadata['file_name'] = original_filename
                doc.metadata['file_path'] = original_filename
        
        config = getattr(settings, "REMOTE_POSTGRES_CONFIG", {})
        
        table_name = get_safe_table_name(self.project_id)
        
        # Configure Vector Store
        vector_store = PGVectorStore.from_params(
            database=config.get("NAME", "postgres"),
            host=config.get("HOST", "localhost"),
            port=config.get("PORT", "5432"),
            user=config.get("USER", "postgres"),
            password=config.get("PASSWORD", ""),
            table_name=table_name,
            embed_dim=3072 # Standard for gemini-embedding-001
        )
        
        storage_context = StorageContext.from_defaults(vector_store=vector_store)
        node_parser = select_node_parser(file_path, strategy=strategy)
        
        # Create Index
        index = VectorStoreIndex.from_documents(
            documents, 
            storage_context=storage_context,
            embed_model=self.embed_model,
            transformations=[node_parser]
        )
        return index

def get_vector_store(project_id):
    config = getattr(settings, "REMOTE_POSTGRES_CONFIG", {})
    table_name = get_safe_table_name(project_id)
    return PGVectorStore.from_params(
        database=config.get("NAME", "postgres"),
        host=config.get("HOST", "localhost"),
        port=config.get("PORT", "5432"),
        user=config.get("USER", "postgres"),
        password=config.get("PASSWORD", ""),
        table_name=table_name,
        embed_dim=3072
    )


def check_structural_quality(filepath: str) -> None:
    """
    Evaluate structural quality of extracted text using gemini-2.5-flash-lite.
    Raises ValueError if score is 7 or lower.
    """
    from llama_index.core import SimpleDirectoryReader
    from google import genai
    from google.genai import types
    import json

    # Extract first 1000 characters from file
    docs = SimpleDirectoryReader(input_files=[filepath]).load_data()
    full_text = "\n".join([d.text for d in docs])
    snippet = full_text[:1000]

    # Call Gemini to score quality
    api_key = os.getenv("GOOGLE_API_KEY", "")
    client = genai.Client(api_key=api_key)

    prompt = f"""You are a Data Quality Inspector. Review the following text snippet extracted from a document. 
Determine if the text structure is intact and readable, or if the layout parser failed.

Look for these failure signs:
- Words mashed together without spaces (e.g., "TheCompanyReport2024")
- Words that do not have any meaning 
- Shattered sentences from misread columns (e.g., "Revenue $5M Introduction to")
- Excessive raw font artifact codes (e.g., "CID:12 CID:44")

Score the text quality from 1 (Complete Garbage) to 10 (Perfectly Readable).
Respond ONLY with a JSON object in this format:
{{"score": int, "reason": "string"}}

Text snippet:
\"\"\"{snippet}\"\"\""""

    response = client.models.generate_content(
        model="gemini-2.5-flash-lite",
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            temperature=0.1
        ),
    )

    try:
        res_data = json.loads(response.text)
        score = int(res_data.get("score", 10))
        reason = res_data.get("reason", "")
        # Log to the server terminal clearly
        logger.info(f"📊 [QUALITY GATE] Document: {filepath} | Score: {score}/10 | Reason: {reason}")
    except Exception as parse_err:
        # Fallback if JSON parsing fails
        score = 10
        reason = f"Fallback due to parsing error: {str(parse_err)}"

    if score <= 7:
        raise ValueError(f"Extraction quality too low (Score: {score}/10). Reason: {reason}")

