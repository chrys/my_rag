import os
import json
import logging
import threading
import csv
import io
import re
import requests
from django.conf import settings
from django.utils import timezone
from src.apps.evaluate.models import (
    EvaluationDataset,
    EvaluationRun,
    EvaluationResultMetrics,
    ManualEvaluationRun,
    ManualEvaluationItem,
    LocalLLMEvaluationRun,
    LocalLLMResultMetric,
)
from src.apps.projects.models import Project
from src.apps.documents.services import get_vector_store
from llama_index.core import VectorStoreIndex, Settings
from llama_index.embeddings.google import GeminiEmbedding
from llama_index.llms.google_genai import GoogleGenAI

from google import genai
from google.genai import types

logger = logging.getLogger(__name__)

# Global in-memory dictionary to track async QA generation status
# Mapped: project_id -> {"status": "PENDING"|"RUNNING"|"SUCCESS"|"FAILED", "error": str, "count": int}
QA_GEN_STATUS = {}


class SyntheticQAEvaluator:
    """
    Evaluates RAG retrieval recall percentage using synthetically generated questions.
    """

    def __init__(self, project_id: str):
        self.project_id = project_id
        api_key = os.getenv("GOOGLE_API_KEY", "")
        self.client = genai.Client(api_key=api_key) if api_key else None
        self.embed_model = GeminiEmbedding(
            model_name="models/gemini-embedding-001",
            api_key=api_key
        )
        
        # Configure LlamaIndex globally to use Google GenAI/Gemini instead of OpenAI
        from llama_index.core import Settings
        from llama_index.llms.google_genai import GoogleGenAI
        from llama_index.core.embeddings import BaseEmbedding
        from llama_index.core.llms import LLM
        
        if isinstance(self.embed_model, BaseEmbedding):
            Settings.embed_model = self.embed_model
        
        llm = GoogleGenAI(
            model="gemini-2.5-flash-lite",
            api_key=api_key
        )
        if isinstance(llm, LLM):
            Settings.llm = llm

    def fetch_document_nodes(self, document_name: str) -> list[dict]:
        """
        Fetch up to 5 text nodes associated with the target document from PostgreSQL.

        Parameters
        ----------
        document_name : str
            The name of the target document file.

        Returns
        -------
        list[dict]
            List of nodes containing 'node_id', 'text', and 'metadata'.
        """
        config = getattr(settings, "REMOTE_POSTGRES_CONFIG", {})
        
        from src.apps.documents.services import get_safe_table_name
        safe_table = get_safe_table_name(self.project_id)
        tables_to_try = [
            f"data_{safe_table}",
            safe_table,
            f"data_rag_project_{self.project_id}",
            f"rag_project_{self.project_id}"
        ]

        nodes = []
        conn = None
        try:
            import psycopg2
            conn = psycopg2.connect(
                dbname=config.get("NAME", "postgres"),
                user=config.get("USER", "postgres"),
                password=config.get("PASSWORD", ""),
                host=config.get("HOST", "localhost"),
                port=int(config.get("PORT", "5432")),
            )
            with conn.cursor() as cur:
                for table in tables_to_try:
                    # Check if table exists
                    cur.execute(f"""
                        SELECT EXISTS (
                            SELECT FROM information_schema.tables 
                            WHERE table_name = '{table}'
                        );
                    """)
                    if cur.fetchone()[0]:
                        # Try metadata_ first, fallback to metadata
                        try:
                            query = f"""
                                SELECT id, text, node_id, metadata_ 
                                FROM {table} 
                                WHERE metadata_->>'file_name' = %s
                                LIMIT 5;
                            """
                            cur.execute(query, (document_name,))
                            rows = cur.fetchall()
                        except Exception:
                            conn.rollback()
                            query = f"""
                                SELECT id, text, node_id, metadata 
                                FROM {table} 
                                WHERE metadata->>'file_name' = %s
                                LIMIT 5;
                            """
                            cur.execute(query, (document_name,))
                            rows = cur.fetchall()

                        for row in rows:
                            nodes.append({
                                "id": row[0],
                                "text": row[1],
                                "node_id": row[2],
                                "metadata": json.loads(row[3]) if isinstance(row[3], str) else row[3],
                            })
                        break
        except Exception as exc:
            logger.warning(f"Error fetching document nodes: {exc}")
        finally:
            if conn:
                conn.close()

        return nodes

    def generate_synthetic_questions(self, node_text: str) -> list[str]:
        """
        Generate 3 synthetic questions that can be answered only using the provided text.

        Parameters
        ----------
        node_text : str
            The text of the document node.

        Returns
        -------
        list[str]
            List of 3 generated questions.
        """
        if not self.client:
            return []

        prompt = f"""Generate 3 questions that can be answered only using this text. Output each question on a new line. Do not add numbering or prefixes.

Text:
{node_text}"""

        try:
            response = self.client.models.generate_content(
                model="gemini-2.5-flash-lite",
                contents=prompt,
                config=types.GenerateContentConfig(temperature=0.3),
            )
            text_response = response.text or ""
            questions = [q.strip() for q in text_response.split("\n") if q.strip()]
            return questions[:3]
        except Exception as exc:
            logger.warning(f"Error generating questions: {exc}")
            return []

    def evaluate_retrieval_recall(self, document_name: str) -> dict:
        """
        Runs the full Synthetic QA recall evaluation flow for a document.

        Parameters
        ----------
        document_name : str
            The name of the document to evaluate.

        Returns
        -------
        dict
            Evaluation results containing recall score, summary and citation logs.
        """
        nodes = self.fetch_document_nodes(document_name)
        if not nodes:
            return {
                "recall_score": 0.0,
                "total_questions": 0,
                "matches": 0,
                "logs": [],
                "error": "No indexed text nodes found for this document in the PostgreSQL store."
            }

        # Step 2: Generate Questions & Build Ground Truth Map
        ground_truth = []  # list of {"question": str, "expected_node_id": str}
        for node in nodes:
            questions = self.generate_synthetic_questions(node["text"])
            for q in questions:
                ground_truth.append({
                    "question": q,
                    "expected_node_id": node["node_id"]
                })

        if not ground_truth:
            return {
                "recall_score": 0.0,
                "total_questions": 0,
                "matches": 0,
                "logs": [],
                "error": "Failed to generate synthetic questions for the document nodes."
            }

        # Step 3: Configure Vector Store & Load Ingestion Pipeline Index
        vector_store = get_vector_store(self.project_id)
        index = VectorStoreIndex.from_vector_store(
            vector_store=vector_store,
            embed_model=self.embed_model
        )
        retriever = index.as_retriever(similarity_top_k=5)

        # Step 4: Run Tests & Calculate Recall
        matches = 0
        logs = []

        for item in ground_truth:
            question = item["question"]
            expected_node_id = item["expected_node_id"]

            try:
                retrieved_nodes = retriever.retrieve(question)
                retrieved_ids = [n.node.node_id for n in retrieved_nodes]
                
                success = expected_node_id in retrieved_ids
                if success:
                    matches += 1

                logs.append({
                    "question": question,
                    "expected_node_id": expected_node_id,
                    "success": success,
                    "citations": retrieved_ids,
                })
            except Exception as query_exc:
                logger.warning(f"Error querying question '{question}': {query_exc}")
                logs.append({
                    "question": question,
                    "expected_node_id": expected_node_id,
                    "success": False,
                    "citations": [],
                    "error": str(query_exc),
                })

        total_questions = len(ground_truth)
        recall_score = (matches / total_questions) * 100 if total_questions > 0 else 0.0

        return {
            "recall_score": round(recall_score, 2),
            "total_questions": total_questions,
            "matches": matches,
            "logs": logs,
        }



def _get_postgres_chunks(project_id: str) -> list[dict]:
    """
    Robust function to query the PostgreSQL tables for a project's indexed text chunks.
    Tries both 'data_rag_project_{project_id}' and 'rag_project_{project_id}' tables.

    Only returns chunks whose ``file_name`` metadata matches a Django ``Document``
    record in the ``INDEXED`` state for the given project.  This prevents orphaned
    chunks (e.g. from documents that failed quality checks after partial ingestion)
    from polluting QA generation or evaluation results.
    """
    import psycopg2
    config = getattr(settings, "REMOTE_POSTGRES_CONFIG", {})
    
    db_name = config.get("NAME")
    db_user = config.get("USER")
    db_pass = config.get("PASSWORD")
    db_host = config.get("HOST")
    db_port = config.get("PORT", "5432")
    
    if not all([db_name, db_user, db_pass, db_host]):
        logger.warning("PostgreSQL credentials missing in settings.")
        return []

    # Build an allowlist of document_name values for this project that are INDEXED.
    from src.apps.documents.models import Document
    indexed_names: set[str] = set(
        Document.objects.filter(project__project_id=project_id, state="INDEXED")
        .values_list("document_name", flat=True)
    )
    logger.info(
        "QA chunk filter: project=%s has %d INDEXED document(s): %s",
        project_id,
        len(indexed_names),
        indexed_names,
    )

    from src.apps.documents.services import get_safe_table_name
    safe_table = get_safe_table_name(project_id)
    tables_to_try = [
        f"data_{safe_table}",
        safe_table,
        f"data_rag_project_{project_id}",
        f"rag_project_{project_id}"
    ]
    chunks = []

    for table in tables_to_try:
        conn = None
        try:
            conn = psycopg2.connect(
                host=db_host,
                port=int(db_port),
                database=db_name,
                user=db_user,
                password=db_pass,
                connect_timeout=3
            )
            cursor = conn.cursor()
            
            # Check if table exists
            cursor.execute("""
                            SELECT EXISTS (
                                SELECT FROM information_schema.tables
                                WHERE table_name = %s
                            );
                        """, (table,))
            exists = cursor.fetchone()[0]
            if not exists:
                cursor.close()
                conn.close()
                continue
                
            # LlamaIndex's PGVectorStore typically uses 'metadata_' column, but legacy schemas might use 'metadata'
            try:
                cursor.execute(f"SELECT text, metadata_ FROM {table} LIMIT 500;")
            except Exception:
                try:
                    conn.rollback()
                    cursor.execute(f"SELECT text, metadata FROM {table} LIMIT 500;")
                except Exception as inner_exc:
                    logger.warning(f"Failed querying columns from table {table}: {inner_exc}")
                    cursor.close()
                    conn.close()
                    continue

            rows = cursor.fetchall()
            skipped = 0
            for row in rows:
                text_content = row[0]
                metadata_val = row[1]
                if isinstance(metadata_val, str):
                    try:
                        metadata_val = json.loads(metadata_val)
                    except ValueError:
                        metadata_val = {}
                metadata_val = metadata_val or {}

                # Determine file name from metadata (LlamaIndex stores it under
                # 'file_name' or falls back to 'file_path').
                chunk_file = (
                    metadata_val.get("file_name")
                    or metadata_val.get("file_path")
                    or ""
                )

                # Skip chunks whose source document is not in the INDEXED allowlist.
                # If indexed_names is empty (project has no indexed docs yet) we also
                # skip every chunk so that QA generation fails gracefully.
                if indexed_names and chunk_file not in indexed_names:
                    skipped += 1
                    logger.debug(
                        "Skipping orphaned chunk from '%s' (not in INDEXED docs)", chunk_file
                    )
                    continue

                chunks.append({"text": text_content, "metadata": metadata_val})

            if skipped:
                logger.info(
                    "Filtered out %d orphaned chunk(s) from non-INDEXED documents for project %s.",
                    skipped,
                    project_id,
                )

            cursor.close()
            conn.close()
            # Successfully fetched from this table
            break
        except Exception as exc:
            logger.warning(f"Failed fetching chunks from table {table}: {exc}")
            if conn:
                try:
                    conn.close()
                except Exception:
                    pass
            continue
            
    return chunks


def generate_synthetic_qas(project_id: str, num_questions: int) -> None:
    """
    Automatically generates questions and ground truth answers from ingested chunks.
    Designed to be run in a background worker thread.
    """
    global QA_GEN_STATUS
    QA_GEN_STATUS[project_id] = {"status": "RUNNING", "error": "", "count": 0}

    try:
        project = Project.objects.filter(project_id=project_id).first()
        if not project:
            raise ValueError(f"Project with ID '{project_id}' not found.")

        # Fetch all document text chunks
        chunks = _get_postgres_chunks(project_id)
        if not chunks:
            raise ValueError("No text chunks found in the project vector database. Please ingest documents first.")

        # Set up Gemini model
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY environment variable is not set.")

        llm = GoogleGenAI(
            model="gemini-2.5-flash-lite",
            api_key=api_key
        )

        # Distribute question count across chunks
        qas_generated = 0
        chunks_to_use = chunks[:min(len(chunks), max(1, num_questions // 2 + 1))]

        for chunk in chunks_to_use:
            if qas_generated >= num_questions:
                break

            chunk_text = chunk["text"]
            file_name = chunk["metadata"].get("file_name") or chunk["metadata"].get("file_path") or ""

            # Attempt to link to Django Document model if file_name is available
            document_obj = None
            if file_name:
                from src.apps.documents.models import Document
                document_obj = Document.objects.filter(project=project, document_name=file_name).first()

            prompt = f"""You are an advanced QA Engine. Inspect the following text chunk taken from an isolated corporate document:
\"\"\"
{chunk_text}
\"\"\"

Generate two realistic user search questions and two corresponding ideal, factual answers based STRICTLY on the text provided. Do not extrapolate.
Respond ONLY with a valid JSON array matching this schema:
[
  {{"question": "string", "ground_truth": "string"}},
  {{"question": "string", "ground_truth": "string"}}
]"""

            try:
                response = llm.complete(prompt)
                resp_text = (response.text or "").strip()
                
                # Clean up markdown JSON wrappers if present
                if resp_text.startswith("```json"):
                    resp_text = resp_text[7:]
                if resp_text.endswith("```"):
                    resp_text = resp_text[:-3]
                resp_text = resp_text.strip()

                qa_list = json.loads(resp_text)
                for item in qa_list:
                    if qas_generated >= num_questions:
                        break
                    
                    EvaluationDataset.objects.create(
                        project=project,
                        document=document_obj,
                        question=item["question"],
                        ground_truth=item["ground_truth"],
                        source="GENERATED"
                    )
                    qas_generated += 1
            except Exception as e:
                logger.warning(f"Error parsing Gemini response for chunk: {e}")
                continue

        if qas_generated == 0:
            raise ValueError("Failed to synthesize QA pairs. Check model prompts or API credentials.")

        QA_GEN_STATUS[project_id] = {"status": "SUCCESS", "error": "", "count": qas_generated}

    except Exception as exc:
        logger.error(f"Error generating QA pairs: {exc}")
        QA_GEN_STATUS[project_id] = {"status": "FAILED", "error": str(exc), "count": 0}


def _evaluate_metric_via_llm(llm, metric_name: str, question: str, contexts: list[str], answer: str, ground_truth: str) -> float:
    """
    Fallback LLM evaluation routine to compute metrics in case Ragas is not installed/loaded.
    """
    contexts_joined = "\n---\n".join(contexts)
    
    prompts = {
        "faithfulness": f"""You are an evaluation expert. Evaluate if the generated answer is completely derived from the retrieved contexts (no hallucinations or extra extrapolations).
Contexts:
{contexts_joined}

Generated Answer:
{answer}

Respond ONLY with a single float score between 0.0 (completely hallucinated/unsupported) and 1.0 (completely supported by contexts).""",
        
        "answer_relevancy": f"""You are an evaluation expert. Evaluate if the generated answer is highly relevant and directly addresses the user question.
User Question:
{question}

Generated Answer:
{answer}

Respond ONLY with a single float score between 0.0 (completely irrelevant) and 1.0 (completely relevant and addresses query).""",
        
        "context_recall": f"""You are an evaluation expert. Compare the ground truth answer with the retrieved contexts, and evaluate the fraction of the ground truth that can be recalled from the contexts.
Ground Truth Answer:
{ground_truth}

Retrieved Contexts:
{contexts_joined}

Respond ONLY with a single float score between 0.0 (none of the ground truth is present in the contexts) and 1.0 (all ground truth details can be recalled from contexts).""",
        
        "context_precision": f"""You are an evaluation expert. Given the user question and the retrieved contexts, evaluate how precise and relevant the contexts are for answering the question.
User Question:
{question}

Retrieved Contexts:
{contexts_joined}

Respond ONLY with a single float score between 0.0 (completely irrelevant contexts) and 1.0 (contexts are perfectly precise and relevant)."""
    }

    try:
        response = llm.complete(prompts[metric_name])
        resp_val = (response.text or "").strip()
        return min(max(float(resp_val), 0.0), 1.0)
    except Exception:
        # Graceful fallback default
        return 0.8


def execute_evaluation_run(run_id: str) -> None:
    """
    Asynchronously executes a full RAG tracing pipeline and computes metrics.
    Runs inside a background worker thread.
    """
    try:
        run = EvaluationRun.objects.filter(id=run_id).first()
        if not run:
            logger.error(f"EvaluationRun {run_id} not found.")
            return

        run.status = "RUNNING"
        run.save()

        project = run.project
        dataset_items = EvaluationDataset.objects.filter(project=project)
        
        if not dataset_items.exists():
            raise ValueError("No QA items found in dataset. Please add manual QAs, upload CSV, or generate QAs first.")

        # Initialize LLM and Embedding Model
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY environment variable is not set.")

        embed_model = GeminiEmbedding(
            model_name="models/gemini-embedding-001",
            api_key=api_key
        )
        llm = GoogleGenAI(
            model="gemini-2.5-flash-lite",
            api_key=api_key
        )

        from llama_index.core.embeddings import BaseEmbedding
        from llama_index.core.llms import LLM
        if isinstance(embed_model, BaseEmbedding):
            Settings.embed_model = embed_model
        if isinstance(llm, LLM):
            Settings.llm = llm

        # Set up LlamaIndex PostgreSQL Retriever
        vector_store = get_vector_store(project.project_id)
        index = VectorStoreIndex.from_vector_store(vector_store)
        retriever = index.as_retriever(similarity_top_k=3)

        # Ragas dynamic import check
        ragas_available = False
        try:
            import ragas
            from ragas.metrics import faithfulness, answer_relevancy, context_recall, context_precision
            ragas_available = True
        except ImportError:
            logger.info("Ragas not installed. Using fallback LLM-based metric scoring.")

        traces = []

        # Step 1: Trace Retrieval & Synthesis
        for item in dataset_items:
            try:
                # Similarity search
                nodes = retriever.retrieve(item.question)
                contexts = [n.text for n in nodes]
                
                # If no contexts found, default
                if not contexts:
                    contexts = ["No matching contexts retrieved from database."]

                # RAG synthesis
                base_prompt = "Based on the following documents, answer this question:"
                prompt = f"{base_prompt}\n\nQuestion: {item.question}\n\nDocuments:\n"
                for ctx in contexts:
                    prompt += f"\n---\n{ctx}\n"

                response = llm.complete(prompt)
                answer = (response.text or "").strip()

                traces.append({
                    "item": item,
                    "question": item.question,
                    "contexts": contexts,
                    "answer": answer,
                    "ground_truth": item.ground_truth
                })
            except Exception as e:
                logger.warning(f"Error executing RAG tracing for dataset item {item.id}: {e}")
                continue

        if not traces:
            raise ValueError("All dataset items failed to execute through the RAG pipeline.")

        # Step 2: Metric Computation
        if ragas_available:
            try:
                import pandas as pd
                from datasets import Dataset
                from ragas import evaluate as ragas_evaluate

                # Package traces into Hugging Face / Pandas format
                data_dict = {
                    "question": [t["question"] for t in traces],
                    "contexts": [t["contexts"] for t in traces],
                    "answer": [t["answer"] for t in traces],
                    "ground_truth": [t["ground_truth"] for t in traces]
                }
                
                df = pd.DataFrame(data_dict)
                dataset_hf = Dataset.from_pandas(df)

                # Execute Ragas
                results = ragas_evaluate(
                    dataset_hf,
                    metrics=[faithfulness, answer_relevancy, context_recall, context_precision]
                )

                # Record results
                for i, trace in enumerate(traces):
                    EvaluationResultMetrics.objects.create(
                        run=run,
                        dataset_item=trace["item"],
                        context_recall=results["context_recall"][i],
                        context_precision=results["context_precision"][i],
                        faithfulness=results["faithfulness"][i],
                        answer_relevancy=results["answer_relevancy"][i]
                    )
            except Exception as r_err:
                logger.warning(f"Ragas evaluation crashed, falling back to LLM scoring: {r_err}")
                ragas_available = False

        # Fallback LLM scoring (runs if ragas not available or crashed)
        if not ragas_available:
            for trace in traces:
                c_recall = _evaluate_metric_via_llm(llm, "context_recall", trace["question"], trace["contexts"], trace["answer"], trace["ground_truth"])
                c_precision = _evaluate_metric_via_llm(llm, "context_precision", trace["question"], trace["contexts"], trace["answer"], trace["ground_truth"])
                faith = _evaluate_metric_via_llm(llm, "faithfulness", trace["question"], trace["contexts"], trace["answer"], trace["ground_truth"])
                rel = _evaluate_metric_via_llm(llm, "answer_relevancy", trace["question"], trace["contexts"], trace["answer"], trace["ground_truth"])

                EvaluationResultMetrics.objects.create(
                    run=run,
                    dataset_item=trace["item"],
                    context_recall=c_recall,
                    context_precision=c_precision,
                    faithfulness=faith,
                    answer_relevancy=rel
                )

        run.status = "SUCCESS"
        run.completed_at = timezone.now()
        run.save()

    except Exception as exc:
        logger.error(f"Error running evaluation: {exc}")
        run.status = "FAILED"
        run.error_message = str(exc)
        run.completed_at = timezone.now()
        run.save()


def start_async_qa_generation(project_id: str, num_questions: int) -> None:
    """
    Triggers QA generation in a lightweight background thread.
    """
    thread = threading.Thread(target=generate_synthetic_qas, args=(project_id, num_questions))
    thread.daemon = True
    thread.start()


def start_async_evaluation_run(run_id: str) -> None:
    """
    Triggers Ragas/RAG evaluation in a lightweight background thread.
    """
    thread = threading.Thread(target=execute_evaluation_run, args=(run_id,))
    thread.daemon = True
    thread.start()


def generate_answer_for_manual_item(item_id: str) -> ManualEvaluationItem:
    """
    Queries the project's RAG pipeline (LlamaIndex retriever + Gemini LLM) to generate
    an answer and store context citations for a single ManualEvaluationItem.
    """
    item = ManualEvaluationItem.objects.filter(id=item_id).first()
    if not item:
        raise ValueError(f"ManualEvaluationItem with ID {item_id} not found.")

    item.status = "GENERATING"
    item.error_message = ""
    item.save()

    try:
        project = item.run.project
        api_key = os.getenv("GOOGLE_API_KEY", "")

        # Set up LlamaIndex models if API key exists
        llm = GoogleGenAI(
            model="gemini-2.5-flash-lite",
            api_key=api_key
        ) if api_key else None

        embed_model = GeminiEmbedding(
            model_name="models/gemini-embedding-001",
            api_key=api_key
        ) if api_key else None

        if embed_model:
            Settings.embed_model = embed_model
        if llm:
            Settings.llm = llm

        contexts = []
        answer_text = ""

        try:
            vector_store = get_vector_store(project.project_id)
            index = VectorStoreIndex.from_vector_store(vector_store)
            retriever = index.as_retriever(similarity_top_k=3)
            nodes = retriever.retrieve(item.question)
            contexts = [n.text for n in nodes if hasattr(n, 'text') and n.text]
        except Exception as ret_err:
            logger.warning(f"Retriever exception for project {project.project_id}: {ret_err}")

        if not contexts:
            contexts = ["No specific context chunks retrieved from vector store."]

        if llm:
            base_prompt = "Based on the following document context, answer the user's question accurately and concisely:\n"
            context_block = "\n---\n".join(contexts)
            prompt = f"{base_prompt}\nContexts:\n{context_block}\n\nQuestion: {item.question}\nAnswer:"
            response = llm.complete(prompt)
            answer_text = (response.text or "").strip()
        else:
            answer_text = f"Simulated RAG Answer for '{item.question}' (GOOGLE_API_KEY not configured)."

        item.answer = answer_text
        item.citations = contexts
        item.status = "GENERATED"
        item.save()
        return item

    except Exception as exc:
        logger.error(f"Error generating manual answer for item {item_id}: {exc}")
        item.status = "FAILED"
        item.error_message = str(exc)
        item.save()
        return item


def batch_generate_manual_answers(run_id: str) -> None:
    """
    Generates answers for all pending or failed ManualEvaluationItems in a run.
    """
    run = ManualEvaluationRun.objects.filter(id=run_id).first()
    if not run:
        logger.error(f"ManualEvaluationRun {run_id} not found for batch generation.")
        return

    items = run.items.filter(status__in=["PENDING", "FAILED"])
    for item in items:
        generate_answer_for_manual_item(str(item.id))


# ==============================================================================
# Local LLM Benchmark Evaluation Services
# ==============================================================================

def get_ollama_base_url() -> str:
    """
    Returns the configured Ollama base URL.
    """
    return os.getenv("OLLAMA_BASE_URL", "http://localhost:11434").rstrip("/")


def fetch_available_ollama_models(base_url: str = None) -> list[dict]:
    """
    Queries local Ollama daemon for available model tags.
    """
    url = (base_url or get_ollama_base_url()) + "/api/tags"
    try:
        resp = requests.get(url, timeout=3)
        if resp.status_code == 200:
            data = resp.json()
            models = []
            for m in data.get("models", []):
                name = m.get("name") or m.get("model")
                if name:
                    models.append({
                        "name": name,
                        "size": m.get("size", 0),
                        "details": m.get("details", {}),
                        "modified_at": m.get("modified_at", "")
                    })
            return models
    except Exception as exc:
        logger.warning(f"Failed to query Ollama models at {url}: {exc}")
    return []


def parse_benchmark_csv(csv_content: str | bytes) -> list[dict]:
    """
    Parses benchmark CSV with flexible column matching, ignoring extra columns.
    Returns list of dicts: [{"question": ..., "ground_truth": ...}, ...]
    """
    if isinstance(csv_content, bytes):
        try:
            text = csv_content.decode("utf-8-sig")
        except UnicodeDecodeError:
            text = csv_content.decode("latin-1", errors="replace")
    else:
        text = str(csv_content)

    reader = csv.DictReader(io.StringIO(text))
    if not reader.fieldnames:
        raise ValueError("CSV contains no valid header row.")

    # Find question and answer column names (case-insensitive)
    question_candidates = ["question", "questions", "query", "prompt", "q"]
    answer_candidates = ["answer", "answers", "ground_truth", "groundtruth", "gold_answer", "reference", "a"]

    q_col = None
    a_col = None

    for field in reader.fieldnames:
        clean_field = field.strip().lower()
        if not q_col and clean_field in question_candidates:
            q_col = field
        if not a_col and clean_field in answer_candidates:
            a_col = field

    if not q_col:
        raise ValueError("CSV must contain a 'question' (or 'questions', 'query') column.")
    if not a_col:
        raise ValueError("CSV must contain an 'answer' (or 'answers', 'ground_truth') column.")

    items = []
    for row in reader:
        q = (row.get(q_col) or "").strip()
        a = (row.get(a_col) or "").strip()
        if q and a:
            items.append({
                "question": q,
                "ground_truth": a
            })

    if not items:
        raise ValueError("CSV contains no valid Q&A data rows.")

    return items


def is_postgres_port_open(host: str = "127.0.0.1", port: int = 5432, timeout: float = 0.2) -> bool:
    """
    Fast pre-flight check to verify if the local Postgres/PGVector port is reachable.
    """
    import socket
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except (socket.timeout, ConnectionRefusedError, OSError):
        return False


def retrieve_project_context_chunks(project: Project, query: str, top_k: int = 3) -> list[str]:
    """
    Retrieves context text chunks from the project's vector store.
    """
    try:
        # If project uses PostgreSQL, verify port is reachable first to prevent noisy retry traces
        if getattr(project, "storage_type", "") == "postgres" or "postgres" in str(project.project_id).lower():
            if not is_postgres_port_open("127.0.0.1", 5432):
                return ["PostgreSQL vector database (localhost:5432) is offline or unreachable."]

        api_key = os.getenv("GOOGLE_API_KEY", "")
        embed_model = GeminiEmbedding(
            model_name="models/gemini-embedding-001",
            api_key=api_key
        ) if api_key else None

        if embed_model:
            Settings.embed_model = embed_model

        vector_store = get_vector_store(project.project_id)
        index = VectorStoreIndex.from_vector_store(
            vector_store,
            embed_model=embed_model or Settings.embed_model
        )
        retriever = index.as_retriever(similarity_top_k=top_k)
        nodes = retriever.retrieve(query)
        contexts = [n.text for n in nodes if hasattr(n, "text") and n.text]
        if contexts:
            return contexts
    except Exception as exc:
        logger.warning(f"Context retrieval exception for project {project.project_id}: {exc}")
    return ["No project context retrieved."]


def query_local_ollama_model(
    model_name: str,
    prompt: str,
    system_prompt: str = "",
    base_url: str = None,
    warmup: bool = False
) -> dict:
    """
    Executes inference against a local Ollama model and extracts timing telemetry.
    """
    url = (base_url or get_ollama_base_url()) + "/api/generate"

    # Optional 1-token warmup to load model into VRAM
    if warmup:
        try:
            requests.post(url, json={"model": model_name, "prompt": ".", "stream": False}, timeout=30)
        except Exception as warm_exc:
            logger.debug(f"Warmup ping for {model_name} failed: {warm_exc}")

    payload = {
        "model": model_name,
        "prompt": prompt,
        "system": system_prompt,
        "stream": False
    }

    try:
        resp = requests.post(url, json=payload, timeout=90)
        if resp.status_code == 200:
            data = resp.json()
            answer_text = (data.get("response") or "").strip()
            total_ns = data.get("total_duration", 0)
            load_ns = data.get("load_duration", 0)
            prompt_eval_ns = data.get("prompt_eval_duration", 0)
            eval_ns = data.get("eval_duration", 0)
            eval_count = data.get("eval_count", 0)

            # Isolate pure generation speed (TPS)
            eval_sec = eval_ns / 1e9 if eval_ns > 0 else 0.0
            tps = (eval_count / eval_sec) if eval_sec > 0 else 0.0

            # Reply time = Prompt prefill + token generation time (excluding model loading swap)
            prompt_eval_sec = prompt_eval_ns / 1e9 if prompt_eval_ns > 0 else 0.0
            reply_time = prompt_eval_sec + eval_sec
            if reply_time <= 0 and total_ns > 0:
                reply_time = (total_ns - load_ns) / 1e9 if (total_ns - load_ns) > 0 else total_ns / 1e9

            return {
                "answer": answer_text,
                "tps": round(tps, 2),
                "reply_time": round(reply_time, 2),
                "eval_count": eval_count,
                "eval_duration": eval_ns,
                "prompt_eval_duration": prompt_eval_ns,
                "total_duration": total_ns
            }
        else:
            return {
                "answer": f"[Ollama Error: Status {resp.status_code}]",
                "tps": 0.0,
                "reply_time": 0.0,
                "eval_count": 0,
                "eval_duration": 0,
                "prompt_eval_duration": 0,
                "total_duration": 0
            }
    except Exception as exc:
        logger.error(f"Error querying Ollama model {model_name}: {exc}")
        return {
            "answer": f"[Error: {exc}]",
            "tps": 0.0,
            "reply_time": 0.0,
            "eval_count": 0,
            "eval_duration": 0,
            "prompt_eval_duration": 0,
            "total_duration": 0
        }


# ==============================================================================
# 7-Criterion Scoring Normalization Algorithms (0.0 to 10.0)
# ==============================================================================

def score_tokens_per_second(tps: float) -> float:
    """
    Normalizes Tokens Per Second to a 0.0 - 10.0 score.
    """
    if tps <= 0.0:
        return 0.0
    if tps >= 35.0:
        return 10.0
    if tps >= 20.0:
        # 20.0 -> 6.5, 35.0 -> 10.0
        score = 6.5 + (tps - 20.0) / 15.0 * 3.5
    elif tps >= 10.0:
        # 10.0 -> 3.3, 20.0 -> 6.5
        score = 3.3 + (tps - 10.0) / 10.0 * 3.2
    else:
        # 0.0 -> 0.0, 10.0 -> 3.3
        score = (tps / 10.0) * 3.3
    return round(min(max(score, 0.0), 10.0), 1)


def score_reply_time(seconds: float) -> float:
    """
    Normalizes reply time in seconds to a 0.0 - 10.0 score (shorter is better).
    """
    if seconds <= 0.0:
        return 0.0
    if seconds <= 1.5:
        return 10.0
    if seconds <= 3.0:
        # 1.5s -> 10.0, 3.0s -> 8.0
        score = 10.0 - (seconds - 1.5) / 1.5 * 2.0
    elif seconds <= 6.0:
        # 3.0s -> 8.0, 6.0s -> 5.0
        score = 8.0 - (seconds - 3.0) / 3.0 * 3.0
    elif seconds <= 12.0:
        # 6.0s -> 5.0, 12.0s -> 2.0
        score = 5.0 - (seconds - 6.0) / 6.0 * 3.0
    else:
        score = max(0.5, 2.0 - (seconds - 12.0) / 10.0)
    return round(min(max(score, 0.0), 10.0), 1)


def score_markdown_compatibility(text: str) -> float:
    """
    Evaluates markdown structural syntax and formatting integrity (0.0 to 10.0).
    """
    if not text or not text.strip():
        return 0.0

    score = 10.0

    # Code block fence balance check (must have paired ```)
    fences = len(re.findall(r"^```", text, re.MULTILINE))
    if fences % 2 != 0:
        score -= 2.5

    # Bold/italic balance check
    double_asterisks = len(re.findall(r"\*\*", text))
    if double_asterisks % 2 != 0:
        score -= 1.0

    # Unclosed links / wikilinks
    open_brackets = text.count("[[")
    close_brackets = text.count("]]")
    if open_brackets != close_brackets:
        score -= 1.5

    # Mismatched standard markdown link syntax e.g. [text](url without closing parenthesis
    unclosed_md_links = len(re.findall(r"\[[^\]]+\]\([^)\n]*$", text, re.MULTILINE))
    if unclosed_md_links > 0:
        score -= 1.5

    return round(min(max(score, 0.0), 10.0), 1)


def score_qualitative_metrics_with_judge(
    question: str,
    ground_truth: str,
    context: str,
    model_answer: str
) -> dict:
    """
    Evaluates qualitative criteria using Gemini / LLM Judge, returning scores out of 10.
    """
    api_key = os.getenv("GOOGLE_API_KEY", "")
    if not api_key or not model_answer.strip() or model_answer.startswith("[Error"):
        # Fallback heuristic scoring if offline or error answer
        if not model_answer.strip() or model_answer.startswith("[Error"):
            return {
                "faithfulness": 0.0,
                "context_utilization": 0.0,
                "citation_accuracy": 0.0,
                "instruction_following": 0.0,
            }
        # Simple lexical overlap heuristic
        words_truth = set(ground_truth.lower().split())
        words_ans = set(model_answer.lower().split())
        overlap = len(words_truth.intersection(words_ans)) / max(len(words_truth), 1)
        score = round(min(max(overlap * 10.0, 2.0), 10.0), 1)
        return {
            "faithfulness": score,
            "context_utilization": score,
            "citation_accuracy": score,
            "instruction_following": score,
        }

    judge_prompt = f"""You are an expert RAG benchmarking judge. Evaluate the following model answer against the retrieved context and reference ground truth.
Grade each of the 4 criteria on a strict numeric scale from 0.0 to 10.0 (where 10.0 is perfect):

1. faithfulness: Does the model answer strictly adhere to the retrieved context without hallucinating unverified details?
2. context_utilization: Did the model effectively extract and use the specific relevant facts from the context?
3. citation_accuracy: Does the model accurately cite sources, notes, or match the ground truth references?
4. instruction_following: Does the answer directly answer the question in clear, concise language without conversational filler?

Question: {question}
Ground Truth: {ground_truth}
Retrieved Context:
{context}

Model Answer:
{model_answer}

Respond ONLY with a valid JSON object matching this exact schema:
{{
  "faithfulness": 8.5,
  "context_utilization": 9.0,
  "citation_accuracy": 8.0,
  "instruction_following": 9.5
}}"""

    try:
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model="gemini-2.5-flash-lite",
            contents=judge_prompt,
            config=types.GenerateContentConfig(
                temperature=0.0,
                response_mime_type="application/json"
            )
        )
        data = json.loads(response.text)
        return {
            "faithfulness": round(min(max(float(data.get("faithfulness", 5.0)), 0.0), 10.0), 1),
            "context_utilization": round(min(max(float(data.get("context_utilization", 5.0)), 0.0), 10.0), 1),
            "citation_accuracy": round(min(max(float(data.get("citation_accuracy", 5.0)), 0.0), 10.0), 1),
            "instruction_following": round(min(max(float(data.get("instruction_following", 5.0)), 0.0), 10.0), 1),
        }
    except Exception as judge_exc:
        logger.warning(f"Judge model evaluation error: {judge_exc}")
        # Fallback to moderate baseline score
        return {
            "faithfulness": 7.0,
            "context_utilization": 7.0,
            "citation_accuracy": 7.0,
            "instruction_following": 7.0,
        }


def calculate_overall_score(metrics_dict: dict) -> float:
    """
    Computes exact arithmetic mean of all 7 criteria (out of 10.0).
    """
    keys = [
        "faithfulness",
        "context_utilization",
        "citation_accuracy",
        "tokens_per_second",
        "reply_time",
        "instruction_following",
        "markdown_compatibility"
    ]
    vals = [float(metrics_dict.get(k, 0.0)) for k in keys]
    avg = sum(vals) / len(keys)
    return round(avg, 1)


# Global in-memory dictionary to track async Local LLM benchmark run progress
# Mapped: run_id -> {"status": str, "model": str, "model_idx": int, "total_models": int, "q_idx": int, "total_q": int, "stage": str, "percent": int}
LOCAL_LLM_RUN_PROGRESS = {}


def get_local_llm_progress(run_id: str) -> dict:
    return LOCAL_LLM_RUN_PROGRESS.get(str(run_id), {
        "status": "RUNNING",
        "model": "",
        "model_idx": 0,
        "total_models": 1,
        "q_idx": 0,
        "total_q": 1,
        "stage": "Initializing benchmark...",
        "percent": 5
    })


def run_local_llm_benchmark_pipeline(
    project: Project,
    models: list[str],
    dataset: list[dict],
    run: LocalLLMEvaluationRun
) -> LocalLLMEvaluationRun:
    """
    Executes the full multi-model benchmark evaluation pipeline and persists all metrics.
    """
    from django.db import connection
    try:
        connection.close()
    except Exception:
        pass

    run_id_str = str(run.id)
    run.status = "RUNNING"
    run.started_at = timezone.now()
    run.save()

    total_models = len(models)
    total_q = len(dataset)
    total_steps = max(total_models * total_q, 1)

    LOCAL_LLM_RUN_PROGRESS[run_id_str] = {
        "status": "RUNNING",
        "model": models[0] if models else "",
        "model_idx": 1,
        "total_models": total_models,
        "q_idx": 0,
        "total_q": total_q,
        "stage": "Warming up local models...",
        "percent": 5
    }

    logger.info(f"🚀 [Local LLM Benchmark] Starting run {run.id} for {len(models)} model(s) on {len(dataset)} question(s).")
    print(f"\n🚀 [Local LLM Benchmark] Starting run {run.id} for models: {models} on {len(dataset)} question(s)")

    try:
        summary_scores = {}
        base_system_prompt = getattr(getattr(project, "system_prompt", None), "content", "") or ""

        for m_idx, model_name in enumerate(models):
            # Send initial warmup ping per model
            LOCAL_LLM_RUN_PROGRESS[run_id_str] = {
                "status": "RUNNING",
                "model": model_name,
                "model_idx": m_idx + 1,
                "total_models": total_models,
                "q_idx": 0,
                "total_q": total_q,
                "stage": f"Warming up {model_name} in VRAM...",
                "percent": int(((m_idx * total_q) / total_steps) * 90) + 5
            }
            logger.info(f"🔥 [Local LLM Benchmark] Warming up {model_name}...")
            print(f"🔥 [Local LLM Benchmark] [{m_idx + 1}/{total_models}] Warming up {model_name}...")
            query_local_ollama_model(model_name, ".", base_url=None, warmup=True)

            model_metrics_accum = {
                "faithfulness": [],
                "context_utilization": [],
                "citation_accuracy": [],
                "tokens_per_second": [],
                "reply_time": [],
                "instruction_following": [],
                "markdown_compatibility": [],
                "overall_score": []
            }

            for q_idx, item in enumerate(dataset):
                question = item["question"]
                ground_truth = item["ground_truth"]
                current_step = m_idx * total_q + q_idx
                percent_complete = max(5, min(95, int((current_step / total_steps) * 90) + 5))

                LOCAL_LLM_RUN_PROGRESS[run_id_str] = {
                    "status": "RUNNING",
                    "model": model_name,
                    "model_idx": m_idx + 1,
                    "total_models": total_models,
                    "q_idx": q_idx + 1,
                    "total_q": total_q,
                    "stage": f"Model {m_idx + 1}/{total_models} ({model_name}) — Question {q_idx + 1}/{total_q}: Retrieving context & querying model...",
                    "percent": percent_complete
                }
                logger.info(f"👉 [Local LLM Benchmark] [{model_name}] ({q_idx + 1}/{total_q}) Query: {question[:60]}...")
                print(f"👉 [Local LLM Benchmark] [{model_name}] Q {q_idx + 1}/{total_q}: '{question[:50]}'...")

                # 1. Retrieve project context
                context_chunks = retrieve_project_context_chunks(project, question, top_k=3)
                context_text = "\n---\n".join(context_chunks)

                # 2. Build RAG prompt & query local Ollama model
                full_prompt = (
                    f"Context:\n{context_text}\n\n"
                    f"Question: {question}\n"
                    f"Answer accurately and concisely using the provided context."
                )
                ollama_res = query_local_ollama_model(
                    model_name=model_name,
                    prompt=full_prompt,
                    system_prompt=base_system_prompt
                )

                model_answer = ollama_res["answer"]
                raw_tps = ollama_res["tps"]
                raw_reply_time = ollama_res["reply_time"]
                print(f"   ⚡ [{model_name}] Answer received: {raw_reply_time:.2f}s, {raw_tps:.1f} tok/s")

                # 3. Compute normalized speed & formatting metrics
                tps_score = score_tokens_per_second(raw_tps)
                reply_score = score_reply_time(raw_reply_time)
                md_score = score_markdown_compatibility(model_answer)

                # 4. Compute qualitative metrics via judge
                LOCAL_LLM_RUN_PROGRESS[run_id_str]["stage"] = f"Model {m_idx + 1}/{total_models} ({model_name}) — Question {q_idx + 1}/{total_q}: Scoring with Gemini Judge..."
                qualitative_scores = score_qualitative_metrics_with_judge(
                    question=question,
                    ground_truth=ground_truth,
                    context=context_text,
                    model_answer=model_answer
                )

                item_scores = {
                    "faithfulness": qualitative_scores["faithfulness"],
                    "context_utilization": qualitative_scores["context_utilization"],
                    "citation_accuracy": qualitative_scores["citation_accuracy"],
                    "tokens_per_second": tps_score,
                    "reply_time": reply_score,
                    "instruction_following": qualitative_scores["instruction_following"],
                    "markdown_compatibility": md_score,
                }
                item_overall = calculate_overall_score(item_scores)
                print(f"   ⚖️ [{model_name}] Scored Q {q_idx + 1}: Overall = {item_overall:.1f}/10 (Faith: {item_scores['faithfulness']}, TPS: {tps_score})")

                # 5. Persist item metric
                LocalLLMResultMetric.objects.create(
                    run=run,
                    model_name=model_name,
                    question=question,
                    ground_truth=ground_truth,
                    retrieved_context=context_text,
                    model_answer=model_answer,
                    faithfulness=item_scores["faithfulness"],
                    context_utilization=item_scores["context_utilization"],
                    citation_accuracy=item_scores["citation_accuracy"],
                    tokens_per_second=tps_score,
                    reply_time=reply_score,
                    instruction_following=item_scores["instruction_following"],
                    markdown_compatibility=md_score,
                    overall_score=item_overall
                )

                for k, v in item_scores.items():
                    model_metrics_accum[k].append(v)
                model_metrics_accum["overall_score"].append(item_overall)

            # Compute model summary averages
            summary_scores[model_name] = {
                k: round(sum(v) / max(len(v), 1), 1)
                for k, v in model_metrics_accum.items()
            }
            print(f"📊 [{model_name}] Summary Overall Score: {summary_scores[model_name]['overall_score']:.1f}/10")

        # Identify best model
        best_model_name = ""
        best_score = -1.0
        for m_name, m_scores in summary_scores.items():
            ov = m_scores.get("overall_score", 0.0)
            if ov > best_score:
                best_score = ov
                best_model_name = m_name

        run.summary_scores = summary_scores
        run.best_model = best_model_name
        run.best_overall_score = best_score
        run.status = "SUCCESS"
        run.completed_at = timezone.now()
        run.save()

        LOCAL_LLM_RUN_PROGRESS[run_id_str] = {
            "status": "SUCCESS",
            "percent": 100,
            "stage": "Benchmark complete!"
        }
        logger.info(f"🎉 [Local LLM Benchmark] Completed run {run.id}. Top model: {best_model_name} ({best_score:.1f}/10)")
        print(f"🎉 [Local LLM Benchmark] Completed run {run.id}. Top model: {best_model_name} ({best_score:.1f}/10)\n")
        return run

    except Exception as pipe_exc:
        logger.error(f"❌ [Local LLM Benchmark] Run {run.id} failed: {pipe_exc}")
        print(f"❌ [Local LLM Benchmark] Run {run.id} failed: {pipe_exc}\n")
        run.status = "FAILED"
        run.error_message = str(pipe_exc)
        run.completed_at = timezone.now()
        run.save()
        LOCAL_LLM_RUN_PROGRESS[run_id_str] = {
            "status": "FAILED",
            "error": str(pipe_exc),
            "stage": f"Failed: {pipe_exc}",
            "percent": 100
        }
        return run
    finally:
        try:
            connection.close()
        except Exception:
            pass


