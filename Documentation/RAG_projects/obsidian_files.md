# Native Obsidian Vault Integration

This document explains how to set up, load, and manage native **Obsidian Vaults** in Postgres RAG projects, and how to keep vector indexing synchronized with changes in your local Obsidian notes.

---

## 1. Overview

Native Obsidian Vault integration allows Postgres RAG projects to directly ingest, sanitize, and query structured Markdown knowledge bases from local Obsidian vaults.

Key capabilities include:
- **Direct Vault Traversal**: Scans markdown notes while respecting automated exclusion rules for system folders, templates, media, and draft notes.
- **Wikilink Sanitization**: Strips Obsidian double-bracket links (`[[Target Note|Custom Alias]]` -> `Custom Alias` and `[[Target Note]]` -> `Target Note`) prior to vector embedding to prevent noisy link syntax from affecting search quality.
- **Metadata Enrichment**: Tags each ingested chunk with parent `folder` name, relative `file_name`, and `project_id`.
- **3-Stage Sync Engine**: Timestamp-based change detection that handles incremental indexing of new notes, re-indexing of modified notes, and automatic purging of deleted notes.

---

## 2. Loading a New Obsidian Vault Project

Follow these steps to connect a local Obsidian vault to a Postgres RAG project:

### Step 1: Create or Select a Project
1. Navigate to the project dashboard (`/rag/dashboard/`).
2. Create a new project or select an existing project with `storage_type=postgres`.

### Step 2: Open the Sources Tab
1. Click on the target project to open the detail view.
2. Select the **Sources** tab.

### Step 3: Switch Source Type to Obsidian
1. Locate the **Source Type** selector at the top of the Sources tab.
2. Toggle the mode from `Document` to `Obsidian`.
3. The UI dynamically switches from the standard document uploader to the **Obsidian Vault Configuration** panel.

### Step 4: Specify the Local Vault Path
1. Enter the absolute file system path to your local Obsidian vault in the **Obsidian Vault Path** input field (e.g. `/Users/username/Obsidian/MyKnowledgeVault`).
2. Click **Index ALL Obsidian files** to trigger the initial full scan and vector ingestion.

---

## 3. Vault Scanning & Exclusion Rules

During indexing, the scanner automatically filters the vault directory to ensure clean data ingestion.

### Automatically Excluded Folders & Files
- **Reserved Folders**: `_resources/`, `Templates/`, `.obsidian/`, `.git/`
- **Non-Markdown & Binary Media**: `.png`, `.jpg`, `.jpeg`, `.gif`, `.pdf`, `.mp4`, `.zip`, etc.
- **Obsidian Special Canvas & Base Files**: `.canvas`, `.base`
- **Draft Notes**: Files starting with `Untitled` (e.g., `Untitled.md`, `Untitled 1.md`)

---

## 4. Keeping Indexing Synchronized

As you modify, create, or delete notes in your Obsidian vault, use the dedicated action controls to maintain alignment between your local files and the Postgres vector database.

### Action Controls

| Action Button | Endpoint | Behavior & Use Case |
|---|---|---|
| **`Index ALL Obsidian files`** | `/rag/projects/<id>/obsidian/index/` | **Full Re-Index**: Scans the entire vault, re-sanitizes all notes, regenerates vector embeddings, and resets file statuses. **Note**: Prompts for user confirmation if notes are already indexed. |
| **`Discover new Files`** | `/rag/projects/<id>/obsidian/sync/` | **Discovery Only**: Scans the local vault directory to detect new files and populate tracking records with status `PENDING`. Does **not** automatically re-index notes into vector storage. |
| **`Index New Files`** | `/rag/projects/<id>/obsidian/index-new/` | **Incremental Ingestion**: Identifies unindexed/pending notes added to the vault directory and ingests only those pending files. Fast execution. |

---

## 5. Note Status Monitoring

The **Obsidian Note Status Table** provides live status tracking for all files in the vault:

- **Relative Path**: Displays file position within the vault (e.g., `Projects/RAG_Design.md`).
- **Parent Folder**: Highlights the immediate parent directory (e.g., `Projects`).
- **Status Badge**:
  - `PENDING`: Discovered, queued for indexing.
  - `INDEXED`: Successfully embedded and stored in PGVector.
  - `FAILED`: Ingestion encountered an error (error details logged).
- **Last Indexed**: Timestamp of the most recent vector update.

---

## 6. Deleting Notes & De-indexing

When you delete a note file from your local Obsidian vault (or move it outside the vault directory):

1. **Automatic Purging on Discovery**:
   Clicking **`Discover new Files`** (or running **`Index ALL Obsidian files`** / **`Index New Files`**) scans the local vault directory and detects that the file is missing from disk.
2. **Database & Vector Store Cleanup**:
   - The `ObsidianFile` tracking record is removed from the system.
   - All vector chunk embeddings associated with the deleted note (`metadata_->>'file_name' = relative_path`) are automatically purged from PostgreSQL PGVector tables.
3. **Status Summary Updates**:
   The project summary cards (`Total`, `Indexed`, `Pending`, `Failed`) update immediately to reflect the lower file count.

---

## 7. API Endpoints & Developer Usage

For programmatic automation or CLI scripts, use the Django REST views:

```http
POST /rag/projects/<project_id>/obsidian/index/
POST /rag/projects/<project_id>/obsidian/index-new/
POST /rag/projects/<project_id>/obsidian/sync/
```

### Python Service Integration

```python
from src.apps.documents.services import sync_obsidian_vault, index_obsidian_vault

# Trigger 3-stage lifecycle sync for a project
sync_results = sync_obsidian_vault(project_id="postgres_abc123")
print(f"Indexed: {sync_results['indexed']}, Deleted: {sync_results['deleted']}")
```
