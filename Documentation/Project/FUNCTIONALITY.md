# Platform Functionality Overview

## Introduction
The My RAG platform is a comprehensive solution designed to transform how businesses interact with their internal knowledge bases. By combining document management with advanced conversational AI, it allows organizations to turn static files into dynamic, queryable intelligence.

## Core Capabilities

### 1. Project Organization
Users can create distinct "Projects" to organize their work. A project acts as a dedicated workspace for a specific topic, department, or client, keeping documents and AI conversations logically separated and easy to manage.

### 2. Flexible Document Ingestion
The platform allows users to upload a variety of business documents (such as reports, manuals, and contracts) into their projects. The system supports multiple backend strategies for storing and processing these documents:
- **Cloud-Powered Search:** Leveraging external providers for massive scale and advanced analytical capabilities.
- **Secure Local Storage:** Processing documents entirely on internal hardware to guarantee absolute data privacy for sensitive information.

### 3. Intelligent Conversational Assistant
At the heart of the platform is an AI-powered chat interface. Users can ask complex, natural language questions about the documents within their project. The AI analyzes the uploaded files and provides accurate, conversational answers, significantly reducing the time spent searching for information.

### 4. Grounded Responses and Citations
To build trust and ensure accuracy, the AI is designed to base its answers strictly on the provided documents. Furthermore, it supplies citations for its answers, pointing users to the exact files where the information was found.

### 5. Custom AI Personas
Businesses can configure "System Prompts" for each project. This allows administrators to give the AI specific instructions, defining its role, tone, and the rules it must follow when answering questions (e.g., instructing the AI to act as a legal assistant or a technical support agent).

### 6. Performance Evaluation
The platform includes built-in quality assurance tools. Users can create test datasets (questions and expected answers) to evaluate the AI's accuracy and performance, ensuring the system consistently meets business standards.

### 7. Project Parameters & Sources Configuration
Each project exposes configurable parameters under the **Parameters** and **Sources** tabs:

#### Parameters Tab
- **Is Active (`is_active`)** — `[ACTIVE]`
  - Soft-activation flag for projects and API keys. Used in database queries (`.filter(is_active=True)`) across admin views and API endpoints to enable or deactivate projects without hard deleting records.
- **Synthesizer (`synthesizer`)** — `[TODO: Placeholder]`
  - Boolean configuration toggle on the `Project` model designed to enable/disable answer synthesis. Rendered in admin metadata panels ([chat_workflow.html](file:///Users/chrys/Projects/my_rag/templates/admin/chat_workflow.html)), but not yet wired to bypass main chat LLM generation.
- **Document Parsing (`document_parsing`)** — `[IMMUTABLE / TODO]`
  - Choice field for document extraction backends (`markitdown`). Document ingestion in `LlamaIndexIngestionPipeline` currently defaults to `SimpleDirectoryReader`. **Note: Cannot be changed after the first source is indexed; disabled in admin when documents exist.**
- **Chunking Strategies** — `[ACTIVE / DOCUMENT LEVEL]`
  - Text chunking is configured at the **Document level** (`Document.chunking_strategy`) with `auto_detect` as the default parser. Specific parsers include Markdown Header Splitter, Code/AST Splitter, Hierarchical (Parent-Child), and Sentence Boundary.
- **Embedding Models (`embedding_model`)** — `[IMMUTABLE / ACTIVE]`
  - Choice field for vector embedding models (`gemini-1`). `gemini-1` (`models/gemini-embedding-001` with 3072 dimensions) is active and used in vector store ingestion. **Note: Cannot be changed after the first source is indexed; disabled in admin when documents exist.**
- **Custom Prompt (`custom_prompt` / `custom_prompt_text`)** — `[ACTIVE]`
  - Custom system prompt behavior is **ACTIVE** via the related `SystemPrompt` model ([models.py](file:///Users/chrys/Projects/my_rag/src/apps/projects/models.py#L171)) and admin `custom_prompt_text` textarea. Automatically injects saved prompts into chat queries.
- **Use MarkItDown (`use_markitdown`)** — `[IMMUTABLE / TODO]`
  - Boolean flag intended to enable Microsoft's MarkItDown pipeline for converting complex files into Markdown prior to ingestion. **Note: Cannot be changed after the first source is indexed; disabled in admin when documents exist.**

#### Sources Tab
- **Use Structural Grading (`use_structural_grading`)** — `[ACTIVE]`
  - Fully active quality gate ([services.py](file:///Users/chrys/Projects/my_rag/src/apps/documents/services.py#L82)) located under the **Sources** tab. Extracts a 1,000-character sample during document upload and uses `gemini-2.5-flash-lite` to score text layout quality (1–10). Extractions scoring $\le 7$ (garbled text, broken layout, CID artifacts) fail quality inspection and are rejected.


