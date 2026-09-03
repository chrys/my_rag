# Chunking Options for RAG Projects

This document provides a comprehensive guide to the text chunking architecture and strategy options available for RAG (Retrieval-Augmented Generation) projects in this application.

---

## 1. Overview & Architecture

Chunking is the process of breaking down large documents into smaller, coherent text passages (nodes) prior to vector embedding and indexing. In RAG systems, effective chunking directly affects:
- **Retrieval Precision**: Matching the exact passage answering the query rather than broad irrelevant context.
- **Context Window Management**: Fitting the most relevant content into the LLM context without exceeding limits or diluting signal.
- **Synthesizer Quality**: Preserving semantic structure (headers, code functions, paragraphs) so answers are coherent and accurate.

### Document-Level Processing Model

Chunking is configured and executed at the **Document Level** (`Document.chunking_strategy`). Because RAG projects typically contain mixed file formats (code, documentation, raw text, PDFs), chunking is tailored per document with **`⚡ Auto-Detect`** as the default strategy.

```
┌────────────────────────────────────────────────────────┐
│                   Document Upload                      │
│        (Optional manual strategy override)             │
└──────────────────────────┬─────────────────────────────┘
                           │
                           ▼
┌────────────────────────────────────────────────────────┐
│             Structural Quality Gate                    │
│      (Gemini 2.5 Flash-Lite score inspection)          │
└──────────────────────────┬─────────────────────────────┘
                           │
                           ▼
┌────────────────────────────────────────────────────────┐
│               select_node_parser()                     │
│    (Strategy selection / Auto-detect by extension)     │
└──────┬───────────────┬──────────────────┬──────────────┘
       │               │                  │
       ▼               ▼                  ▼
┌─────────────┐ ┌──────────────┐ ┌────────────────┐
│  Markdown   │ │     Code     │ │  Hierarchical  │ ...
│ NodeParser  │ │   Splitter   │ │  (Parent/Child)│
└──────┬──────┘ └──────┬───────┘ └────────┬───────┘
       │               │                  │
       └───────────────┼──────────────────┘
                       ▼
┌────────────────────────────────────────────────────────┐
│           VectorStoreIndex Ingestion                   │
│   (Gemini Embedding 001 ➔ PGVector PostgreSQL)         │
└────────────────────────────────────────────────────────┘
```

---

## 2. Document Chunking Strategies

When uploading documents, the system defaults to auto-detecting the optimal parser based on file extension, or users can explicitly choose a strategy.

| Strategy Key | Display Name | Target Formats / Use Cases | Underlying LlamaIndex Parser | Key Parameters |
| :--- | :--- | :--- | :--- | :--- |
| `auto_detect` | **⚡ Auto-Detect (Recommended)** | All supported formats (`.md`, `.py`, `.js`, `.ts`, `.html`, `.pdf`, `.txt`) | Dynamically resolves to `MarkdownNodeParser`, `CodeSplitter`, or `SentenceSplitter` | Dynamic |
| `markdown` | **Markdown Header Splitter** | Documentation, Obsidian vaults, Markdown notes (`.md`) | `MarkdownNodeParser.from_defaults()` | Header hierarchy (`#`, `##`, `###`) |
| `code` | **Code / AST Splitter** | Source code files (`.py`, `.js`, `.ts`, `.html`) | `CodeSplitter` | `chunk_lines=40`, `chunk_lines_overlap=5`, `max_chars=1500` |
| `hierarchical` | **Hierarchical / Parent-Child** | Long legal agreements, dense technical manuals, academic papers | `HierarchicalNodeParser.from_defaults()` | Multi-tier `chunk_sizes=[1024, 256]` |
| `sentence` | **Sentence / Paragraph Splitter** | General text, narrative articles, FAQs, raw notes (`.txt`, `.pdf`) | `SentenceSplitter` | `chunk_size=512`, `chunk_overlap=50` |

---

### Strategy Deep-Dive

#### 1. Auto-Detect (`auto_detect`) - Recommended Default
- **Behavior**: Inspects the incoming file extension and automatically assigns the most appropriate parser:
  - `.md` $\rightarrow$ `MarkdownNodeParser`
  - `.py`, `.js`, `.ts`, `.html` $\rightarrow$ `CodeSplitter`
  - `.txt`, `.pdf`, and all others $\rightarrow$ `SentenceSplitter`
- **UI Experience**: Real-time extension preview banner informs the user which parser will be utilized upon file selection.

#### 2. Markdown Header Splitter (`markdown`)
- **Parser**: `llama_index.core.node_parser.MarkdownNodeParser`
- **How it works**: Splits documents along markdown heading boundaries (`#`, `##`, `###`, etc.).
- **Benefits**: Retains parent-child relationship between sections; ensures headers remain attached to their respective paragraphs, preventing fragmented context.

#### 3. Code / AST Splitter (`code`)
- **Parser**: `llama_index.core.node_parser.CodeSplitter`
- **Configuration**:
  - `chunk_lines`: 40 lines
  - `chunk_lines_overlap`: 5 lines
  - `max_chars`: 1500 characters
  - `language`: `python`, `javascript`, `typescript`, `html` (mapped from file extension)
- **Benefits**: Preserves function declarations, classes, and complete blocks instead of arbitrarily cutting code in mid-statement.

#### 4. Hierarchical (Parent-Child) Splitter (`hierarchical`)
- **Parser**: `llama_index.core.node_parser.HierarchicalNodeParser`
- **Configuration**: `chunk_sizes=[1024, 256]`
- **How it works**: Generates smaller 256-token child nodes for high-precision semantic search retrieval while linking back to 1024-token parent nodes for synthesis context.
- **Benefits**: Prevents context starvation during LLM generation without sacrificing query similarity precision.

#### 5. Sentence & Paragraph Splitter (`sentence`)
- **Parser**: `llama_index.core.node_parser.SentenceSplitter`
- **Configuration**: `chunk_size=512`, `chunk_overlap=50`
- **How it works**: Splits text into ~512 token chunks respecting natural paragraph and sentence punctuation boundaries rather than hard character cuts.
- **Benefits**: Versatile, clean baseline parser for unstructured text, meeting notes, articles, and documentation.

---

## 3. Backend Implementation & Execution Flow

### Ingestion Pipeline (`src/apps/documents/services.py`)

During document upload, `LlamaIndexIngestionPipeline` orchestrates parsing, embedding, and vector storage:

```python
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
```

### Error Recovery & Fallbacks
- **Graceful Fallback**: If an unsupported format, parsing exception, or tree-sitter compilation error occurs, the ingestion pipeline automatically falls back to `SentenceSplitter(chunk_size=512, chunk_overlap=50)`.
- **Quality Gate**: Prior to chunking, `check_structural_quality()` scans the raw extracted text with `gemini-2.5-flash-lite`. If layout corruption or CID font artifacts are detected (score $\le 7/10$), upload is halted before creating invalid chunks.

---

## 4. Strategy Selection Guide

| Document Content | Recommended Chunking Strategy | Rationale |
| :--- | :--- | :--- |
| **API Docs & Tech Specs** | `markdown` | Preserves parameter tables, code blocks, and section hierarchies under relevant endpoints. |
| **Source Code Repositories** | `code` | Retains full functions and class definitions; avoids syntax fragmentation across chunks. |
| **Contracts, Legal & Compliance** | `hierarchical` | Small leaf nodes capture specific clauses; parent nodes preserve contract definitions and context. |
| **Articles, FAQs, Knowledge Base** | `sentence` or `auto_detect` | Maintains clean narrative continuity without abrupt sentence truncations. |
| **Mixed Multi-Format Projects** | `auto_detect` | Automatically applies the best parser per file format without manual configuration. |

---

## 5. Related Documentation

- [rag_projects.md](file:///Users/chrys/Projects/my_rag/Documentation/RAG_projects/rag_projects.md) — Postgres RAG architecture, vector storage, and query flows.
- [document_parsers.md](file:///Users/chrys/Projects/my_rag/Documentation/Project/document_parsers.md) — User interface guide, extension preview banners, and testing workflows.
- [obsidian_files.md](file:///Users/chrys/Projects/my_rag/Documentation/RAG_projects/obsidian_files.md) — Handling linked markdown notes and metadata extraction.
