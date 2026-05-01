# Initial Concept
Django-based RAG system.

# Product Definition - My RAG

## Vision
My RAG is a robust, Django-powered platform for Retrieval-Augmented Generation (RAG). It enables users to upload documents, create search projects (local or Google File Search), and interact with their data using advanced LLMs (Gemini, Ollama). The platform aims to bridge the gap between private data and powerful language models with a focus on ease of use and extensibility.

## Target Users
- Developers and researchers working with RAG.
- Organizations needing a private, local-first document interaction tool.
- Users who want to integrate Google File Search with LLM workflows.

## Core Features
- **Project Management:** Create and manage different RAG projects.
- **Document Ingestion:** Support for PDF and other document types. Ingestion for RAG projects now powered by LlamaIndex.
- **Hybrid Search:** Local project storage, Google File Search, and PostgreSQL-based RAG indexing using LlamaIndex.
- **Multi-LLM Support:** Integration with Google Gemini and Ollama.
- **Evaluation Dashboard:** Tools to evaluate the performance and accuracy of RAG outputs.
- **User Management:** Secure access and project isolation.

## Design Philosophy
- **Scalability:** Built on Django for high performance and reliability.
- **Modularity:** App-based architecture for easy expansion.
- **Privacy:** Support for local LLMs and embeddings (Ollama, FAISS).
