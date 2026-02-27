# API Documentation

## Overview
My RAG exposes a RESTful API built with Django Rest Framework (DRF). This API provides programmatic access to manage projects, documents, chat messages, evaluations, and API usage.

## Base URL
All API endpoints are prefixed with: `/api/`

## Authentication
Currently, most endpoints have `permission_classes = [AllowAny]` configured, meaning they are publicly accessible for development purposes. Future updates (Phase 3) will introduce stricter user management and authentication.

## Core Endpoints

The API is structured around Django apps using DRF `DefaultRouter` to automatically generate standard CRUD routes for ViewSets.

### 1. Projects (`/api/projects/`)
Manages both Local and Google File Search projects.

- `GET /api/projects/` - List all projects
- `POST /api/projects/` - Create a new project
- `GET /api/projects/{id}/` - Get project details. Supports lookup by primary key, `project_id`, or `external_store_id`.
- `PUT /api/projects/{id}/` - Update a project
- `DELETE /api/projects/{id}/` - Delete a project
- **Custom Actions:**
  - `GET /api/projects/active/` - List only active projects
  - `GET /api/projects/by_storage/?type={storage_type}` - Filter projects by their storage type (e.g., local, google_file_search)
  - `GET|POST /api/projects/{id}/prompt/` - Get or set the system prompt for a specific project
  - `GET /api/projects/{id}/documents/` - List all documents associated with a specific project

### 2. System Prompts (`/api/prompts/`)
Manages the system instructions given to the LLM for specific projects.

- `GET /api/prompts/` - List all prompts
- `POST /api/prompts/` - Create a prompt
- `GET /api/prompts/{id}/` - Get prompt details
- `PUT /api/prompts/{id}/` - Update a prompt
- `DELETE /api/prompts/{id}/` - Delete a prompt

### 3. Documents (`/api/documents/`)
Manages uploaded files and their metadata.

- `GET /api/documents/` - List all documents
- `POST /api/documents/` - Upload a new document
- `GET /api/documents/{id}/` - Get document details
- `DELETE /api/documents/{id}/` - Delete a document and its embeddings/index from the storage backend.

### 4. Chat Messages (`/api/messages/`)
Manages the chat history and interactions.

- `GET /api/messages/` - List chat messages
- `POST /api/messages/` - Create a new message (This endpoint triggers the RAG query pipeline to generate an LLM response)
- `GET /api/messages/{id}/` - Get message details

### 5. Evaluation (`/api/datasets/`, `/api/results/`)
Manages QA datasets and the results of RAG evaluation runs.

- **Datasets (`/api/datasets/`)**
  - Standard CRUD endpoints for managing test questions and expected answers.
- **Results (`/api/results/`)**
  - Standard CRUD endpoints for storing metrics generated during evaluation runs.

### 6. API Management (`/api/keys/`, `/api/usage/`)
Manages API keys and usage tracking.

- Standard CRUD endpoints for tracking and managing API limits.

## Data Formats
- The API consumes and produces standard JSON.
- Request validation is handled by DRF Serializers (e.g., `ProjectCreateSerializer`, `DocumentSerializer`).
