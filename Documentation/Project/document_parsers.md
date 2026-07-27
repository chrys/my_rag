# Document-Type Specific Node Parsers

## Executive Summary & Business Value

Previously, the application applied a single, generic chunking method to all uploaded files regardless of their format. This often broke code functions across chunk boundaries or lost header relationships in Markdown files, reducing AI answer accuracy.

With **Document-Type Specific Node Parsers**, the system intelligently selects the optimal parsing strategy based on the file type (`.pdf`, `.md`, `.py`, `.js`, `.txt`) or explicit user preference during upload. This preserves critical document structure, resulting in:
- **Higher Retrieval Accuracy**: AI models retrieve complete code blocks, structured sections, and contextually rich parent passages.
- **Improved Answer Quality**: Reduces broken or incomplete AI responses when querying technical docs, code repositories, or structured contracts.
- **Flexible Control**: Gives administrators and content managers the choice to rely on automatic format detection or manually select a custom parsing strategy.

---

## Supported Parsing Strategies

| Strategy | Ideal File Types | Business Benefit |
| :--- | :--- | :--- |
| **⚡ Auto-Detect (Recommended)** | All supported files | Automatically identifies file extension and applies the best parser without requiring manual configuration. Displays real-time UI guidance on the target parser. |
| **Markdown Header Splitter** | `.md` files, documentation guides | Preserves heading hierarchy (`#`, `##`, `###`) so AI retrieves complete thematic sections. |
| **Code / AST Splitter** | `.py`, `.js`, `.ts`, `.html` | Structure-aware code parsing that keeps functions, classes, and HTML tags together. |
| **Hierarchical (Parent-Child)** | `.pdf` files, long contracts, research papers | Creates small search nodes linked to larger context blocks, delivering exact answers with full context. |
| **Sentence Boundary** | `.txt` files, FAQs, raw notes | Clean text chunking respecting natural sentence and paragraph endings. |

---

## Interactive UI Guidance & Manual Overrides

To ensure transparency during document ingestion:
1. **Live Extension Preview**: When a file is selected (e.g., `script.py` or `readme.md`), the UI immediately displays a live banner explaining which parser will be automatically used (e.g., `⚡ Auto-Detected File Extension (.py): System will use Code / AST Splitter`).
2. **Manual Strategy Overrides**: Content managers can change the strategy dropdown at any time. When changed from Auto-Detect, the UI displays a clear `Manual Override Active` indicator, letting the user know they are manually dictating the chunking algorithm.
3. **Document List Badges**: Document cards display `⚡ Auto-Detect` or `⚙️ [Custom Strategy Name]` tags so administrators can verify how every uploaded file was parsed.

---

## How to Test & Verify

### 1. Document Upload Workflow Test
1. Log in to the application and navigate to your **Project Sources** or **Document Manager**.
2. Click **Choose File** and select a test file (e.g., a `.md` Markdown file or a `.py` Python code file).
3. Observe the live **Auto-Detect Information Banner**:
   - It will update in real time to show the detected extension and target parser.
4. (Optional) Change the **Chunking Strategy** dropdown to manually override the strategy (e.g., *Markdown Header* or *Code / AST*).
5. Click **Upload**.

### 2. Verify Parser Badge Indicators
1. Once uploaded, review the document card in the document list.
2. Verify that a distinct **Strategy Badge** tag (`⚡ Auto-Detect` or `⚙️ Strategy Name`) appears next to the document status.

### 3. Verify AI Retrieval Quality in Chat
1. Open the **RAG Chat** interface for the project.
2. Ask a question targeting specific functions in uploaded code files or specific headings in uploaded Markdown guides.
3. Check the source references in the AI response to confirm that context nodes were cleanly extracted without broken code snippets or cut-off sentences.
