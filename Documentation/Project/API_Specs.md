# My RAG Programmatic API Specification

This document provides a comprehensive programmatic API specification for managing projects, uploading documents, and running RAG chat queries.

All endpoints support standard **HTTP Basic Authentication** to allow seamless integration from command-line tools (`curl`), background worker scripts, or external microservices.

---

## 🔐 Authentication & Global Setup

* **Base URL:** `http://127.0.0.1:8000` (Local Development) or your custom production domain (e.g., `http://www.example.com`).
* **Authentication Method:** HTTP Basic Auth. Pass credentials using the standard `Authorization` header or `curl -u`.
* **Example Credentials (used in examples below):**
  * **Username:** `chrys-rag`
  * **Password:** `Password123!` (Pass as `'chrys-rag:Password123!'` in terminal to avoid Zsh history expansion issues with the `!` character).

---

## 🛠️ Endpoints Reference

### 1. Create a Project
Creates a new RAG project. The storage backend determines how embeddings are managed:
* `local`: Indexes documents in local vector storage (SQLite metadata).
* `postgres`: Indexes documents in a PostgreSQL database using `pgvector` and `txtai`/`LlamaIndex`.
* `google`: Indexes documents using Google File Search.

#### Endpoint Specifications
* **Method:** `POST`
* **Path:** `/rag/api/projects/`
* **Content-Type:** `application/json`

#### Request Payload
```json
{
  "project_id": "postgres_local_test_rag",
  "display_name": "Local API Test RAG",
  "storage_type": "postgres",
  "description": "API-created project for local testing."
}
```

#### Example Request (`curl`)
```bash
curl -X POST http://127.0.0.1:8000/rag/api/projects/ \
  -u 'chrys-rag:Password123!' \
  -H "Content-Type: application/json" \
  -d '{
    "project_id": "postgres_local_test_rag",
    "display_name": "Local API Test RAG",
    "storage_type": "postgres",
    "description": "API-created project for local testing."
  }'
```

#### Successful Response (`201 Created`)
```json
{
  "id": 1,
  "project_id": "postgres_local_test_rag",
  "display_name": "Local API Test RAG",
  "storage_type": "postgres",
  "description": "API-created project for local testing.",
  "created_at": "2026-05-27T14:32:16Z",
  "external_store_id": null
}
```

#### Error Response (`400 Bad Request` - Validation Error)
```json
{
  "project_id": [
    "Project with this project_id already exists."
  ]
}
```

---

### 2. Delete a Project
Deletes a project record from the metadata database and unlinks associated assets.

#### Endpoint Specifications
* **Method:** `DELETE`
* **Path:** `/rag/api/projects/<project_id>/`

#### Example Request (`curl`)
```bash
curl -X DELETE http://127.0.0.1:8000/rag/api/projects/postgres_local_test_rag/ \
  -u 'chrys-rag:Password123!'
```

#### Successful Response (`204 No Content`)
*Empty Response Body*

#### Error Response (`404 Not Found`)
```json
{
  "detail": "No Project matches the given query."
}
```

---

### 3. Upload a File to a Project
Uploads and indexes a document file to be parsed, chunked, and stored inside the project's vector database. 

#### Endpoint Specifications
* **Method:** `POST`
* **Path:** `/rag/documents/<project_id>/upload/`
* **Content-Type:** `multipart/form-data`
* **Supported Extensions:** `.pdf`, `.txt`, `.md`

#### Request Form Data
* **Field Name:** `file`
* **Field Value:** A raw binary/text file stream.

#### Example Request (`curl`)
```bash
curl -X POST http://127.0.0.1:8000/rag/documents/postgres_local_test_rag/upload/ \
  -u 'chrys-rag:Password123!' \
  -F "file=@/Users/chrys/Documents/paul_graham_essay.txt"
```

> [!NOTE]
> The `@` symbol preceding the path is required by `curl` to specify a local file upload stream.

#### Successful Response (`200 OK`)
```json
{
  "status": "success",
  "document": "paul_graham_essay.txt"
}
```

#### Error Response (`400 Bad Request` - Unsupported format)
```json
{
  "error": "Unsupported file type: .json. Supported file types are: .pdf, .txt, .md"
}
```

#### Error Response (`500 Internal Server Error` - Database connection offline)
```json
{
  "error": "Upload failed: PostgreSQL VPS Connection failed: connection to server at \"127.0.0.1\", port 5432 failed: Connection refused"
}
```

---

### 4. Chat with a Project
Asks questions and retrieves answers from the context stored in a specific project's indexed files. The system handles vector retrieval, LLM prompt assembly, and source attribution automatically.

#### Endpoint Specifications
* **Method:** `POST`
* **Path:** `/rag/api/chat/`
* **Content-Type:** `application/json`

#### Request Payload
```json
{
  "store_id": "postgres_local_test_rag",
  "query": "What was the first startup the author founded?",
  "system_prompt": "You are a professional research assistant. Keep your responses highly concise."
}
```

#### Example Request (`curl`)
```bash
curl -X POST http://127.0.0.1:8000/rag/api/chat/ \
  -u 'chrys-rag:Password123!' \
  -H "Content-Type: application/json" \
  -d '{
    "store_id": "postgres_local_test_rag",
    "query": "What was the first startup the author founded?",
    "system_prompt": "You are a professional research assistant. Keep your responses highly concise."
  }'
```

#### Successful Response (`200 OK`)
```json
{
  "user_message": "What was the first startup the author founded?",
  "bot_response": "The first startup founded by the author was Viaweb, an online store builder.",
  "bot_response_html": "<p>The first startup founded by the author was <strong>Viaweb</strong>, an online store builder.</p>",
  "source_documents": [
    "paul_graham_essay.txt"
  ]
}
```

#### Error Response (`403 Forbidden` - Ownership Check Failed)
```json
{
  "error": "Forbidden"
}
```
*(Occurs if the authenticated user is not the owner/creator of the requested project).*

---

### 5. Retrieve All Documents of a Project
Lists metadata and status of all documents indexed or attempted for ingestion under a specific project.

#### Endpoint Specifications
* **Method:** `GET`
* **Path:** `/rag/api/documents/by_project/`
* **Query Parameters:**
  * `project_id` (string, required): The unique project identifier.

#### Example Request (`curl`)
```bash
curl -X GET 'http://127.0.0.1:8000/rag/api/documents/by_project/?project_id=postgres_local_test_rag' \
  -u 'chrys-rag:Password123!'
```

#### Successful Response (`200 OK`)
```json
[
  {
    "id": 12,
    "project": 1,
    "document_name": "paul_graham_essay.txt",
    "display_name": "paul_graham_essay.txt",
    "external_document_id": null,
    "mime_type": "text/plain",
    "file_size": 75003,
    "state": "INDEXED",
    "indexed_at": "2026-05-27T14:36:26Z",
    "error_message": "",
    "created_at": "2026-05-27T14:36:24Z"
  }
]
```

#### Error Response (`400 Bad Request` - Missing `project_id`)
```json
{
  "error": "project_id required"
}
```

