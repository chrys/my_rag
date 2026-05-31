# Some day 

## Local RAG
### Missing text chunking for Local RAG (local_rag.py)
The Vulnerability: Embedding models (like embeddinggemma) have strict, hard-coded token limits. If a user uploads a 40-page PDF, passing it as a single string will either crash the local Ollama instance entirely, truncate 90% of the document invisibly, or generate a "diluted" vector that fails to retrieve specific facts.

The Fix: You must implement a chunking layer (like LlamaIndex's SentenceSplitter or TokenTextSplitter) to slice the raw text into ~512 token blocks with a 50-token overlap before calculating the embeddings.

### Massive Performance Bottleneck: Synchronous Disk I/O
In local_rag.py, you have explicitly disabled the global caching dictionary (_rag_engines = {}), forcing get_rag_engine() to create a fresh instance every time it is called.

The Vulnerability: Every time a user sends a chat message or uploads a file, your system synchronously executes _load_index(). This reads the entire faiss_index.bin and metadata.json from your Mac mini's hard drive directly into RAM before it even begins processing the user's request. As your database grows to hundreds of megabytes, this will cause crippling latency and block your asynchronous server workers.

The Fix: You must re-enable memory caching for the FAISS index during the application lifecycle, or migrate the local vector storage to a system that natively handles memory-mapped I/O (like ChromaDB or PostgreSQL with pgvector).

### Concurrency Data Corruption: JSON State Management
Your prompt_storage.py and local_project_storage.py currently handle state by executing json.dump() directly to files in the configuration/ directory.

The Vulnerability: If you look at your rag-api-gunicorn.conf.py, you have configured workers = 2. This means you have multiple Python processes running in parallel. If two different users (or API calls) attempt to update a custom prompt or add a local project at the exact same millisecond, both workers will try to overwrite prompts.json simultaneously. This creates a race condition that will inevitably corrupt the JSON file, wiping out all project data.

The Fix: Since you already have a PostgreSQL instance running successfully (verified by your test_postgres_connection.py script), you must completely delete these JSON storage classes and migrate the state management into your robust Django ORM models (SystemPrompt and Project).