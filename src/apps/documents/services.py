import os
from django.conf import settings
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, StorageContext
from llama_index.vector_stores.postgres import PGVectorStore
from llama_index.embeddings.google import GeminiEmbedding

import logging
logger = logging.getLogger(__name__)

import re


def sanitize_obsidian_markdown(text: str) -> str:
    """
    Sanitize Obsidian-specific Markdown syntax:
    - [[Target Note|Custom Alias]] -> Custom Alias
    - [[Target Note]] -> Target Note
    """
    if not text:
        return text
    # Convert [[Target Note|Custom Alias]] -> Custom Alias
    text = re.sub(r'\[\[[^\]|]+\|([^\]]+)\]\]', r'\1', text)
    # Convert [[Target Note]] -> Target Note
    text = re.sub(r'\[\[([^\]]+)\]\]', r'\1', text)
    return text


def scan_obsidian_vault(vault_path: str) -> list[dict]:
    """
    Traverse an Obsidian vault directory and discover valid markdown note files.
    Applies exclusion rules:
    - Skips reserved folders: _resources/, Templates/, .obsidian/, .git/
    - Skips media & binary files: .png, .jpg, .jpeg, .gif, .pdf
    - Skips proprietary files: .canvas, .base
    - Skips draft notes: filenames starting with 'Untitled' (e.g. Untitled 1.md)
    """
    if not vault_path or not os.path.exists(vault_path) or not os.path.isdir(vault_path):
        raise ValueError(f"Vault path '{vault_path}' does not exist or is not a valid directory.")

    try:
        os.listdir(vault_path)
    except PermissionError:
        raise PermissionError(f"Permission denied accessing '{vault_path}'. On macOS, grant Full Disk Access to your Terminal/IDE in System Settings > Privacy & Security, or choose a directory inside your workspace/home folder.")

    excluded_dirs = {'_resources', 'templates', '.obsidian', '.git'}
    excluded_exts = {'.png', '.jpg', '.jpeg', '.gif', '.pdf', '.canvas', '.base'}

    discovered_files = []

    try:
        for root, dirs, files in os.walk(vault_path):
            # Prune excluded directories from traversal
            dirs[:] = [d for d in dirs if d.lower() not in excluded_dirs and not d.startswith('.')]

            for file_name in files:
                ext = os.path.splitext(file_name)[1].lower()
                base_name = os.path.splitext(file_name)[0]

                # Skip binary, media, canvas, hidden, and untitled draft files
                if ext in excluded_exts or file_name.startswith('.'):
                    continue
                if base_name.lower().startswith('untitled'):
                    continue
                if ext != '.md':
                    continue

                abs_path = os.path.join(root, file_name)
                rel_path = os.path.relpath(abs_path, vault_path)

                # Determine immediate parent folder name
                parent_dir = os.path.basename(root)
                folder_name = parent_dir if root != vault_path else 'Root'

                try:
                    mtime = os.path.getmtime(abs_path)
                except OSError:
                    mtime = 0.0

                discovered_files.append({
                    'relative_path': rel_path,
                    'folder_name': folder_name,
                    'absolute_path': abs_path,
                    'file_mtime': mtime
                })
    except PermissionError as pe:
        raise PermissionError(f"Permission denied accessing directory in '{vault_path}': {pe}")

    return discovered_files


def enrich_chunk_metadata(chunk_metadata: dict, folder: str, file_name: str, project_id: str) -> dict:
    """
    Enrich chunk metadata dictionary with folder, file_name, and project_id structural tags.
    """
    metadata = dict(chunk_metadata or {})
    metadata['folder'] = folder
    metadata['file_name'] = file_name
    metadata['project_id'] = project_id
    return metadata


def discover_obsidian_vault_files(source) -> list:
    """
    Stage 1 Discovery: Scan vault directory, sync ObsidianFile records in DB.
    Purges ObsidianFile records for notes deleted from disk.
    Optimized with bulk operations and atomic transaction.
    """
    from django.utils import timezone
    from django.db import transaction
    from src.apps.documents.models import ObsidianFile

    discovered = scan_obsidian_vault(source.vault_path)
    discovered_rel_paths = {d['relative_path']: d for d in discovered}

    with transaction.atomic():
        # Purge records and vector store embeddings for notes deleted on disk
        deleted_files = list(source.files.exclude(relative_path__in=discovered_rel_paths.keys()))
        if deleted_files:
            try:
                from src.postgres_rag import PostgresRAGEngine
                engine = PostgresRAGEngine(project_id=source.project.project_id)
                for d_file in deleted_files:
                    engine.delete_document(d_file.relative_path)
            except Exception as exc:
                logger.warning(f"Failed cleaning up vector entries for deleted obsidian files: {exc}")

        source.files.exclude(relative_path__in=discovered_rel_paths.keys()).delete()

        existing_files = {f.relative_path: f for f in source.files.all()}
        new_objects = []
        update_objects = []

        for item in discovered:
            rel = item['relative_path']
            if rel in existing_files:
                obj = existing_files[rel]
                obj.folder_name = item['folder_name']
                obj.file_mtime = item['file_mtime']
                update_objects.append(obj)
            else:
                new_objects.append(ObsidianFile(
                    obsidian_source=source,
                    relative_path=rel,
                    folder_name=item['folder_name'],
                    file_mtime=item['file_mtime']
                ))

        if new_objects:
            ObsidianFile.objects.bulk_create(new_objects)
        if update_objects:
            ObsidianFile.objects.bulk_update(update_objects, fields=['folder_name', 'file_mtime'])

        source.last_synced_at = timezone.now()
        source.save()

    return list(source.files.all())


def process_obsidian_file_indexing(obsidian_file, project_id: str) -> bool:
    """
    Stage 2 & 3: Read, sanitize Markdown, enrich metadata, run LlamaIndex vector ingestion, update status.
    """
    from django.utils import timezone
    import tempfile

    source = obsidian_file.obsidian_source
    abs_path = os.path.join(source.vault_path, obsidian_file.relative_path)

    if not os.path.exists(abs_path):
        obsidian_file.status = 'FAILED'
        obsidian_file.error_message = "File does not exist on disk."
        obsidian_file.save()
        return False

    try:
        with open(abs_path, 'r', encoding='utf-8', errors='ignore') as f:
            raw_content = f.read()

        sanitized_content = sanitize_obsidian_markdown(raw_content)

        tmp_dir = os.path.join(getattr(settings, 'BASE_DIR', os.getcwd()), 'tmp_test_dir')
        os.makedirs(tmp_dir, exist_ok=True)
        with tempfile.NamedTemporaryFile('w', suffix='.md', encoding='utf-8', delete=False, dir=tmp_dir) as tmp:
            tmp.write(sanitized_content)
            tmp_path = tmp.name

        try:
            pipeline = LlamaIndexIngestionPipeline(project_id=project_id)
            pipeline.index_document(
                file_path=tmp_path,
                original_filename=obsidian_file.relative_path,
                strategy='markdown'
            )
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

        obsidian_file.status = 'INDEXED'
        obsidian_file.last_indexed_at = timezone.now()
        obsidian_file.error_message = ""
        obsidian_file.save()
        return True
    except Exception as e:
        logger.error(f"Failed to index Obsidian file '{obsidian_file.relative_path}': {e}")
        obsidian_file.status = 'FAILED'
        obsidian_file.error_message = str(e)
        obsidian_file.save()
        return False


def run_obsidian_lifecycle(source, mode: str = 'full') -> dict:
    """
    Run 3-stage Obsidian indexing/sync lifecycle.
    - mode='full': Discovers vault notes, re-indexes all valid notes.
    - mode='new': Discovers vault notes, indexes only pending/unindexed notes.
    - mode='sync': Discovers vault notes, purges deleted notes, re-indexes modified/pending notes.
    - mode='discover': Discovers vault notes and populates ObsidianFile tracking records (PENDING), but does NOT automatically index them.
    """
    from django.utils import timezone

    db_files = discover_obsidian_vault_files(source)
    project_id = source.project.project_id

    indexed_count = 0
    failed_count = 0

    if mode != 'discover':
        for obsidian_file in db_files:
            should_index = False
            if mode == 'full':
                should_index = True
            elif mode == 'new':
                should_index = (obsidian_file.status != 'INDEXED')
            elif mode == 'sync':
                should_index = (obsidian_file.status != 'INDEXED') or (obsidian_file.last_indexed_at is None)

            if should_index:
                success = process_obsidian_file_indexing(obsidian_file, project_id)
                if success:
                    indexed_count += 1
                else:
                    failed_count += 1

        total_indexed = source.files.filter(status='INDEXED').count()
        source.project.document_count = total_indexed
        source.project.last_indexed_at = timezone.now()
        source.project.save()

    return {
        'total_files': len(db_files),
        'indexed_count': indexed_count,
        'failed_count': failed_count,
        'mode': mode
    }


def get_safe_table_name(project_id: str) -> str:
    """
    Return a postgres-safe table name under 48 characters to keep "data_" + table name
    and automatically generated index names (e.g. {table_name}_idx_1) under 63 bytes.
    Uses MD5 hash to ensure uniqueness while preserving a readable prefix.
    """
    # Ensure project_id is safe before doing string operations
    project_id = "".join(c for c in project_id if c.isalnum() or c == '_')
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
            parent_dir = os.path.dirname(original_filename)
            folder_name = os.path.basename(parent_dir) if parent_dir else 'Root'
            for doc in documents:
                doc.metadata['file_name'] = original_filename
                doc.metadata['file_path'] = original_filename
                doc.metadata['folder'] = folder_name
                doc.metadata['project_id'] = self.project_id
        
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


def compute_file_sha256(file_path: str) -> str:
    """
    Computes the SHA-256 hash of a file for local deduplication and state registry tracking.
    """
    import hashlib
    sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            sha256.update(chunk)
    return sha256.hexdigest()


def check_document_hygiene(file_path: str, filename: str) -> dict:
    """
    Pre-flight validation gate for uploaded documents:
    - Verifies supported whitelist extensions (.pdf, .txt, .md, .docx, .pptx, .xlsx, .csv, .html, .json).
    - Ensures file is non-empty (>0 bytes) and within 100MB API single-file limit.
    - Tests for PDF/DOCX corruption or DRM encryption.
    """
    import mimetypes

    ext = os.path.splitext(filename)[1].lower()
    allowed_extensions = {".pdf", ".txt", ".md", ".docx", ".pptx", ".xlsx", ".csv", ".html", ".json"}
    
    if ext not in allowed_extensions:
        return {
            "valid": False,
            "error": f"Unsupported file format '{ext}'. Allowed formats: {', '.join(sorted(allowed_extensions))}.",
            "content_hash": None,
            "file_size": 0,
            "mime_type": None
        }

    try:
        file_size = os.path.getsize(file_path)
    except OSError as e:
        return {
            "valid": False,
            "error": f"Unable to access file: {str(e)}",
            "content_hash": None,
            "file_size": 0,
            "mime_type": None
        }

    if file_size == 0:
        return {
            "valid": False,
            "error": "File is empty (0 bytes).",
            "content_hash": None,
            "file_size": 0,
            "mime_type": None
        }

    max_size_bytes = 100 * 1024 * 1024 # 100 MB limit
    if file_size > max_size_bytes:
        return {
            "valid": False,
            "error": f"File size ({file_size / (1024*1024):.1f} MB) exceeds maximum 100 MB limit.",
            "content_hash": None,
            "file_size": file_size,
            "mime_type": None
        }

    # Format integrity & DRM check
    if ext == ".pdf":
        try:
            from pypdf import PdfReader
            reader = PdfReader(file_path)
            if reader.is_encrypted:
                return {
                    "valid": False,
                    "error": "PDF is password-protected or encrypted.",
                    "content_hash": None,
                    "file_size": file_size,
                    "mime_type": "application/pdf"
                }
            if len(reader.pages) == 0:
                return {
                    "valid": False,
                    "error": "PDF file contains 0 pages.",
                    "content_hash": None,
                    "file_size": file_size,
                    "mime_type": "application/pdf"
                }
        except Exception as e:
            return {
                "valid": False,
                "error": f"Corrupted or invalid PDF file: {str(e)}",
                "content_hash": None,
                "file_size": file_size,
                "mime_type": "application/pdf"
            }

    content_hash = compute_file_sha256(file_path)
    mime_type, _ = mimetypes.guess_type(filename)
    if not mime_type:
        mime_type = "application/octet-stream"

    return {
        "valid": True,
        "error": None,
        "content_hash": content_hash,
        "file_size": file_size,
        "mime_type": mime_type
    }


def strip_noisy_artifacts(text: str) -> str:
    """
    Cleans up boilerplate artifacts before ingestion:
    - Strips pagination patterns (e.g., 'Page 1 of 10', '- 1 -', bare page numbers).
    - Strips recurring boilerplate and legal disclaimers.
    - Normalizes excessive blank lines.
    """
    if not text:
        return ""

    lines = text.splitlines()
    cleaned_lines = []

    # Patterns for pagination and noise lines
    pagination_patterns = [
        re.compile(r'^\s*Page\s+\d+(\s+of\s+\d+)?\s*$', re.IGNORECASE),
        re.compile(r'^\s*-\s*\d+\s*-\s*$'),
        re.compile(r'^\s*\d+\s*$'), # Standalone page numbers
        re.compile(r'^\s*(All rights reserved|Confidential|Copyright\s+.*|Terms of Use)\.?\s*$', re.IGNORECASE),
    ]

    for line in lines:
        is_noise = False
        for pat in pagination_patterns:
            if pat.match(line):
                is_noise = True
                break
        if not is_noise:
            cleaned_lines.append(line)

    result = "\n".join(cleaned_lines)
    # Collapse multiple consecutive newlines down to at most 2
    result = re.sub(r'\n{3,}', '\n\n', result)
    return result.strip()


def extract_system_and_file_metadata(file_path: str, filename: str, user=None) -> list[dict]:
    """
    Step 1: Extracts deterministic system & file properties.
    """
    from datetime import datetime
    ext = os.path.splitext(filename)[1].lower()
    
    metadata = [
        {"key": "file_name", "string_value": filename},
        {"key": "file_type", "string_value": ext},
    ]

    try:
        size_bytes = os.path.getsize(file_path)
        metadata.append({"key": "file_size_kb", "numeric_value": round(size_bytes / 1024.0, 1)})
        mtime = os.path.getmtime(file_path)
        created_date = datetime.fromtimestamp(mtime).strftime("%Y-%m-%d")
        metadata.append({"key": "created_date", "string_value": created_date})
    except OSError:
        pass

    if user and hasattr(user, "username") and user.username:
        metadata.append({"key": "uploader", "string_value": str(user.username)})

    if ext == ".pdf":
        try:
            from pypdf import PdfReader
            reader = PdfReader(file_path)
            metadata.append({"key": "page_count", "numeric_value": float(len(reader.pages))})
            if reader.metadata:
                if reader.metadata.author:
                    metadata.append({"key": "author", "string_value": str(reader.metadata.author)[:100]})
                if reader.metadata.title:
                    metadata.append({"key": "title", "string_value": str(reader.metadata.title)[:100]})
        except Exception:
            pass

    return metadata


def extract_ai_metadata_with_gemini_flash(sample_text: str) -> list[dict]:
    """
    Step 2: Content-Aware AI Extraction using gemini-2.5-flash-lite.
    Gracefully falls back to empty list on error.
    """
    if not sample_text or not sample_text.strip():
        return []

    try:
        from google.genai import types
        import json
        from src import google_file_search as gfs

        if not gfs.client:
            return []

        snippet = sample_text[:3000]
        prompt = (
            "Analyze the following document snippet and classify its high-level business metadata.\n"
            "Extract: document_type (e.g. Report, Invoice, Contract, Manual), department (e.g. Finance, Legal, Engineering), and language (ISO 2-letter code).\n"
            "Return ONLY a JSON object with keys: document_type, department, language (and any other relevant single-word attributes).\n\n"
            f"Snippet:\n\"\"\"{snippet}\"\"\""
        )

        response = gfs.client.models.generate_content(
            model="gemini-2.5-flash-lite",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                temperature=0.1
            ),
        )

        if not response or not response.text:
            return []

        data = json.loads(response.text)
        metadata = []
        for k, v in data.items():
            if v is not None and str(v).strip():
                sanitized_k = re.sub(r'[^a-zA-Z0-9_]', '_', str(k).strip().lower())
                if isinstance(v, (int, float)):
                    metadata.append({"key": sanitized_k, "numeric_value": float(v)})
                else:
                    metadata.append({"key": sanitized_k, "string_value": str(v).strip()})
        return metadata
    except Exception as e:
        logger.warning(f"AI metadata pre-extraction failed (falling back gracefully): {e}")
        return []


def format_and_validate_gfs_metadata(metadata_list: list[dict]) -> list[dict]:
    """
    Formats, validates, and caps metadata to conform strictly to GFS constraints:
    - Maximum 20 entries.
    - Mutually exclusive string_value OR numeric_value.
    - Key sanitized to alphanumeric and underscore (<= 40 chars).
    """
    if not metadata_list:
        return []

    formatted = []
    seen_keys = set()

    for item in metadata_list:
        raw_key = item.get("key", "")
        if not raw_key:
            continue

        # Sanitize key: lowercase, letters/numbers/underscores, collapse repeated underscores
        sanitized_key = re.sub(r'[^a-zA-Z0-9_]', '_', str(raw_key).strip().lower())
        sanitized_key = re.sub(r'_+', '_', sanitized_key).strip('_')[:40]
        if not sanitized_key or sanitized_key in seen_keys:
            continue

        entry = {"key": sanitized_key}
        if "numeric_value" in item and item["numeric_value"] is not None:
            try:
                entry["numeric_value"] = float(item["numeric_value"])
            except (ValueError, TypeError):
                entry["string_value"] = str(item["numeric_value"])
        elif "string_value" in item and item["string_value"] is not None:
            entry["string_value"] = str(item["string_value"])[:255]
        elif "value" in item and item["value"] is not None:
            val = item["value"]
            if isinstance(val, (int, float)):
                entry["numeric_value"] = float(val)
            elif isinstance(val, str):
                try:
                    # Check if numeric string
                    if re.match(r'^-?\d+(\.\d+)?$', val.strip()):
                        entry["numeric_value"] = float(val.strip())
                    else:
                        entry["string_value"] = val.strip()[:255]
                except (ValueError, TypeError):
                    entry["string_value"] = val.strip()[:255]
            else:
                entry["string_value"] = str(val)[:255]

        if "string_value" in entry or "numeric_value" in entry:
            seen_keys.add(sanitized_key)
            formatted.append(entry)

        if len(formatted) >= 20:
            break

    return formatted



