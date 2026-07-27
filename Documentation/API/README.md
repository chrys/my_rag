# My RAG Platform API Documentation

## Executive Overview

The **My RAG Platform API** provides a powerful set of RESTful Web services designed to integrate enterprise Retrieval-Augmented Generation (RAG) capabilities into third-party enterprise tools, web applications, customer support portals, and automated workflows.

By leveraging this API, organizations can automate knowledge base management, upload business documentation, execute intelligent conversational queries with verifiable document citations, govern AI behavior through custom system prompts, and continuously monitor model quality using quantitative evaluation datasets.

---

## Business Capabilities

Our API enables organizations to control every phase of the Retrieval-Augmented Generation lifecycle:

### 1. Multi-Tenant Project & Knowledge Base Management
* **Dynamic Knowledge Isolation**: Automatically create and manage distinct AI projects scoped to specific teams, departments, clients, or domain subjects.
* **Flexible Storage Architectures**: Provision projects across varied infrastructure backends—including managed Google File Search (`google`), self-managed PostgreSQL vector storage (`postgres`), or local filesystem stores (`local`).
* **Automated Life-cycle Control**: Query active project registries, filter by storage backend, update metadata, or deprecate inactive knowledge repositories programmatically.

### 2. Document Ingestion & Index Lifecycle Governance
* **Automated Knowledge Ingestion**: Register incoming company documents (PDFs, text, Markdown, Office documents) into target project stores.
* **Real-time Processing States**: Monitor document ingestion stages through transparent state tracking (`PENDING`, `INDEXING`, `INDEXED`, `FAILED`).
* **Automated Index Cleanup**: Deleting a document via the API automatically purges metadata from the relational database and removes embedded vectors from the underlying RAG vector index.

### 3. Conversational RAG & Source Attribution
* **Context-Aware Querying**: Programmatically query knowledge bases to receive accurate, context-grounded AI responses rendered in both raw Markdown and clean HTML.
* **Verifiable Document Citations**: Every response returns a list of source documents (`source_documents`) used to generate the answer, providing complete auditability and eliminating AI hallucinations.
* **Session & History Tracking**: Maintain ongoing conversational context using session identifiers (`session_id`) and retrieve user message histories for auditing or analytics.

### 4. AI Persona & System Prompt Governance
* **Custom AI Instructions**: Define custom system prompts per project to mandate corporate tone, formatting guidelines, safety constraints, and domain specializations.
* **Dynamic Instructions Overrides**: Update project prompts on-the-fly or pass transient instruction overrides per query to adapt AI responses to specific workflow needs.

### 5. Continuous QA, Evaluation & Benchmarking
* **Ground-Truth Dataset Curation**: Programmatically store and manage golden Question-Answer datasets (`EvaluationDataset`) linked to specific knowledge documents.
* **Automated Evaluation Execution**: Trigger automated test runs (`EvaluationRun`) to evaluate the current RAG pipeline against ground-truth datasets.
* **Quantitative Quality Metrics**: Access detailed evaluation metrics (`EvaluationResultMetrics`) including:
  * **Context Recall**: Measures if all relevant reference information was retrieved.
  * **Context Precision**: Measures if only relevant chunks were retrieved.
  * **Faithfulness**: Measures if the answer is strictly derived from retrieved context without fabrication.
  * **Answer Relevancy**: Measures how directly the generated answer satisfies the user query.

### 6. Enterprise API Security & Usage Governance
* **Granular Key Management**: Generate, activate, or revoke secure API keys per application or developer.
* **Usage Analytics & Telemetry**: Track request volumes, response times (`response_time_ms`), HTTP status codes, and IP addresses per endpoint.
* **Performance Telemetry**: Query built-in summary analytics to calculate throughput in the last 24 hours, average latency, and endpoint distribution.

---

## Authentication & Access Control

The API supports three authentication strategies:

1. **API Key Authentication** (Recommended for External Integrations):
   Passed via header: `X-API-Key: <your_api_key>`
2. **HTTP Basic Authentication** (Programmatic Access):
   Passed via standard HTTP Authorization header: `Authorization: Basic <base64_credentials>`
3. **Session Authentication** (Dashboard / Front-end App):
   Standard Django session cookies for authenticated web app users.

---

## Service Endpoints Summary

| Category | Endpoint | Supported HTTP Methods | Business Description |
| :--- | :--- | :--- | :--- |
| **Chat API** | `/rag/api/chat/` | `POST` | Execute RAG query against a project store and receive grounded answer + citations. |
| **Projects** | `/rag/api/projects/` | `GET`, `POST` | List user projects or create a new project. |
| | `/rag/api/projects/{id}/` | `GET`, `PUT`, `PATCH`, `DELETE` | Retrieve, update, or delete project by ID, project_id, or external_store_id. |
| | `/rag/api/projects/{id}/prompt/` | `GET`, `POST` | Fetch or update the system prompt for a project. |
| | `/rag/api/projects/{id}/documents/` | `GET` | List all documents belonging to a project. |
| | `/rag/api/projects/active/` | `GET` | Filter and return only active projects. |
| | `/rag/api/projects/by_storage/?type={type}` | `GET` | Filter projects by storage backend (`local`, `google`, `postgres`). |
| **Prompts** | `/rag/api/prompts/` | `GET`, `POST` | Manage system prompt records across projects. |
| | `/rag/api/prompts/{id}/` | `GET`, `PUT`, `PATCH`, `DELETE` | Retrieve, update, or delete specific system prompt. |
| **Documents** | `/rag/api/documents/` | `GET`, `POST` | List documents or register new document metadata. |
| | `/rag/api/documents/{id}/` | `GET`, `PUT`, `PATCH`, `DELETE` | Retrieve, update, or delete document (clears vector index if `store_id` provided). |
| | `/rag/api/documents/by_project/?project_id={id}` | `GET` | Retrieve documents associated with a project. |
| | `/rag/api/documents/by_state/?state={state}` | `GET` | Filter documents by status (`PENDING`, `INDEXING`, `INDEXED`, `FAILED`). |
| | `/rag/api/documents/indexed/` | `GET` | List all successfully indexed documents. |
| | `/rag/api/documents/failed/` | `GET` | List all failed document ingestions. |
| **Chat Messages** | `/rag/api/messages/` | `GET`, `POST` | List historical messages or create user/bot chat log entries. |
| | `/rag/api/messages/{id}/` | `GET` | Retrieve detailed chat message record. |
| | `/rag/api/messages/by_project/?project_id={id}` | `GET` | Retrieve message history for a specific project. |
| | `/rag/api/messages/by_session/?session_id={id}` | `GET` | Retrieve ordered conversation log for a specific session. |
| | `/rag/api/messages/by_user/` | `GET` | Retrieve message history for the authenticated user. |
| **Evaluation Datasets** | `/rag/api/datasets/` | `GET`, `POST` | List or create ground-truth QA dataset entries. |
| | `/rag/api/datasets/{id}/` | `GET`, `PUT`, `PATCH`, `DELETE` | Manage dataset QA pairs. |
| | `/rag/api/datasets/by_project/?project_id={id}` | `GET` | Retrieve QA evaluation dataset for a project. |
| **Evaluation Runs** | `/rag/api/runs/` | `GET`, `POST` | List or launch evaluation benchmark runs. |
| | `/rag/api/runs/{id}/` | `GET`, `PUT`, `DELETE` | View run progress/status, update, or delete run. |
| **Evaluation Metrics** | `/rag/api/results/` | `GET` | List quantitative metrics results across runs. |
| | `/rag/api/results/{id}/` | `GET` | View detailed precision/recall/faithfulness/relevancy metrics. |
| **API Key Governance** | `/rag/api/keys/` | `GET`, `POST` | List API keys or generate a new secret token. |
| | `/rag/api/keys/{id}/` | `GET`, `PUT`, `DELETE` | Inspect, update, or revoke an API key. |
| | `/rag/api/keys/active/` | `GET` | List active API keys for authenticated user. |
| **Usage Analytics** | `/rag/api/usage/` | `GET` | Inspect raw API request logs. |
| | `/rag/api/usage/{id}/` | `GET` | Inspect specific usage log item. |
| | `/rag/api/usage/by_key/?key_id={key_id}` | `GET` | Filter telemetry by API key. |
| | `/rag/api/usage/by_endpoint/?endpoint={ep}` | `GET` | Filter telemetry by API endpoint path. |
| | `/rag/api/usage/summary/` | `GET` | Fetch aggregate usage statistics (24h counts, avg latency, errors). |
