# Technology Stack - My RAG

## Core Technologies
- **Language:** Python 3.x
- **Backend Framework:** Django 6.x
- **API Framework:** Django Rest Framework
- **RAG Framework:** Llama-Index
- **Frontend:** Django Templates, HTMX, Vanilla CSS

## Data Storage
- **Primary Database:** SQLite (for application data)
- **RAG Database:** PostgreSQL (for document storage and embeddings)
- **Vector Store:** PostgreSQL Vector (pgvector) via LlamaIndex

## LLM Integrations
- **Cloud:** Google Gemini
- **Local:** Ollama

## Infrastructure
- **Server:** Gunicorn
- **Deployment:** Shell-based deployment (deploy.sh)
