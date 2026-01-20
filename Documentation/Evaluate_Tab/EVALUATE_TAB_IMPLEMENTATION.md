# Evaluate Tab Implementation

## Overview

The Evaluate Tab enables users to automatically generate Q&A pairs from selected documents and evaluate them using LlamaIndex's evaluation framework.

## User Workflow

1. **Select Project** - User clicks on a project in the left panel
2. **Select File** - User clicks on a file within the project
3. **Select Evaluation Method** - User chooses from dropdown:
   - **Auto Generate** (currently implemented) - Automatically generates Q&A pairs
   - Manual (placeholder for future)
   - DeepEval (placeholder for future)
4. **Click Generate** - Triggers the evaluation pipeline
5. **View Results** - Q&A pairs are displayed below "Generation Results" section

## Backend Architecture

### Main Components

#### 1. **Evaluation Module** (`src/evaluate/llamaindex_dataset_generation.py`)
Modular functions for the evaluation pipeline:

- `init_evaluation(model)` - Initialize GoogleGenAI LLM with API key
- `create_dummy_documents()` - Create sample documents
- `generate_dataset(documents, llm, num_questions_per_chunk)` - Generate Q&A pairs using RagDatasetGenerator
- `define_evaluators(llm)` - Initialize Faithfulness and Relevancy evaluators
- `run_batch_evaluation(queries, responses, evaluators)` - Run batch evaluation
- `print_results(eval_results, queries, responses)` - Display results

#### 2. **Flask API Endpoint** (`src/app.py`)

**Endpoint:** `POST /api/evaluate`

**Request:**
```json
{
  "store_id": "project_id",
  "doc_id": "document_id",
  "method": "auto"
}
```

**Response (Auto Generate):**
```json
{
  "success": true,
  "result": "<html formatted Q&A pairs>",
  "store_id": "project_id",
  "doc_id": "document_id",
  "method": "auto",
  "total_pairs": 10,
  "json_file": "qa_pairs_<timestamp>.json"
}
```

#### 3. **JSON Storage** (`src/evaluate/data/`)

Q&A pairs are automatically saved as JSON files with the following structure:

```json
{
  "metadata": {
    "timestamp": "20260105_160000",
    "store_id": "project_id",
    "doc_id": "document_id",
    "total_pairs": 10
  },
  "qa_pairs": [
    {
      "index": 0,
      "query": "What is LlamaIndex?",
      "response": "LlamaIndex is a data framework..."
    },
    ...
  ]
}
```

**Filename Format:** `qa_pairs_{store_id}_{doc_id}_{timestamp}.json`

#### 4. **Frontend** (`templates/evaluate.html`)

- **Left Panel** - Project and file selection
- **Right Panel** - File information and generation results
- **Results Display** - Shows:
  - Success banner with Q&A pair count
  - Filename where JSON was saved
  - First 5 Q&A pairs in formatted cards
  - "...and X more" indicator if more than 5 pairs

## Data Flow

```
User Selects Project/File
         ↓
Clicks Generate (Auto method)
         ↓
Flask /api/evaluate endpoint
         ↓
init_evaluation() → Load GoogleGenAI LLM
         ↓
create_dummy_documents() → Get sample docs
         ↓
generate_dataset() → Create Q&A pairs (10 pairs)
         ↓
save_qa_pairs_to_json() → Store JSON file
         ↓
Format HTML results
         ↓
Return to Frontend
         ↓
Display Q&A pairs in Evaluate Tab
```

## Key Features

✅ **Async Processing** - Uses asyncio for efficient async operations
✅ **Error Handling** - Comprehensive try-catch blocks with meaningful messages
✅ **JSON Persistence** - All Q&A pairs saved to disk for later reference
✅ **Security** - HTML escaping for safe display
✅ **Modular Design** - Separates concerns into focused functions
✅ **Progress Feedback** - Loading states and success indicators

## File Locations

| Component | Path |
|-----------|------|
| Evaluation module | `src/evaluate/llamaindex_dataset_generation.py` |
| Flask app | `src/app.py` |
| Evaluate template | `templates/evaluate.html` |
| Q&A JSON files | `src/evaluate/data/` |
| Test script | `test_evaluate_imports.py` |

## Current Limitations (Future Enhancements)

1. **Dummy Documents** - Currently uses hardcoded dummy documents; should load from selected file
2. **Limited Evaluation** - Only supports "Auto Generate"; Manual and DeepEval are placeholders
3. **No Score Display** - Evaluation scores not shown (always 0.0 without reference docs)
4. **Single File** - Only one file at a time; batch processing not yet supported

## To Use in Production

### Step 1: Replace Dummy Documents
Update `generate_dataset()` to load content from the selected file instead of dummy documents

### Step 2: Implement Reference-Based Evaluation
Add reference documents to evaluators for meaningful scores:
```python
eval_results = await batch_runner.aevaluate_responses(
    queries=queries,
    responses=responses,
    reference=[doc.text for doc in source_documents]
)
```

### Step 3: Implement Manual Evaluation
Add UI for manual evaluation input and scoring

### Step 4: Implement DeepEval Method
Integrate DeepEval metrics for deeper analysis

## Testing

Run the evaluation module standalone:
```bash
python src/evaluate/llamaindex_dataset_generation.py
```

Test Flask imports:
```bash
python test_evaluate_imports.py
```

Start the Flask app:
```bash
python src/app.py
```

Then navigate to `http://localhost:5000/evaluate` and test the UI workflow.
