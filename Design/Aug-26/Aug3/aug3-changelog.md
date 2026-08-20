# Sprint Changelog (Aug 3)

## Summary of What We Built

### 1. Google File Search Project Setup
- **Enabled Google File Search Projects:** Users can now create projects powered directly by Google File Search.
- **Smart Setting Adjustments:** When Google File Search is selected, the system automatically simplifies the settings by hiding or locking options that do not apply and showing only compatible Google Gemini models (`gemini-2.5-flash-lite`, `gemini-3.5-flash-lite`, `gemini-3.7-flash`).
- **Cleaned Up Duplicate Settings:** Removed the redundant "Use MarkItDown" toggle and consolidated document parsing into a single clear setting.

### 2. Document Quality & File Pre-Checks
- **Pre-Upload Safety Guard:** Added an automatic check before files are processed.
- **Clear Error Notices:** If a user tries to upload an empty (0-byte) file or an unsupported file format, a clear popup appears explaining why the file cannot be uploaded.

### 3. Automatic Tag Suggestions & Review Window
- **Smart Tag Extraction:** When a document is chosen, the system automatically analyzes it and generates helpful tags (such as document type, department, file size, and upload date).
- **Interactive Review Popup:** Users can review the suggested tags, edit them, add custom tags, or delete unneeded ones before confirming the upload.
- **Visual Document Tags:** Uploaded documents now display their tags directly in the document list for quick scanning.

### 4. Duplicate File Detection & Control
- **Duplicate Detection:** If a user attempts to upload a file that already exists in the project, the system detects it immediately.
- **User Choice Prompt:** A popup appears with two clear options:
  - **Skip Upload:** Keeps the existing file and saves upload quota.
  - **Force Re-upload:** Replaces the old indexed document with the newly uploaded version.

### 5. Chat with Google File Search Documents
- **Grounded Chat Responses:** The chat assistant can now answer questions accurately based on documents stored in Google File Search, using the selected Gemini model.
