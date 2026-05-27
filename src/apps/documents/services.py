import os
from django.conf import settings
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, StorageContext
from llama_index.vector_stores.postgres import PGVectorStore
from llama_index.embeddings.google import GeminiEmbedding

class LlamaIndexIngestionPipeline:
    def __init__(self, project_id):
        self.project_id = project_id
        # Configure gemini-embedding-001
        self.embed_model = GeminiEmbedding(
            model_name="models/gemini-embedding-001",
            api_key=os.getenv("GOOGLE_API_KEY")
        )
        
    def index_document(self, file_path):
        # Read the document
        documents = SimpleDirectoryReader(input_files=[file_path]).load_data()
        
        config = getattr(settings, "REMOTE_POSTGRES_CONFIG", {})
        
        # Configure Vector Store
        vector_store = PGVectorStore.from_params(
            database=config.get("NAME", "postgres"),
            host=config.get("HOST", "localhost"),
            port=config.get("PORT", "5432"),
            user=config.get("USER", "postgres"),
            password=config.get("PASSWORD", ""),
            table_name=f"rag_project_{self.project_id}",
            embed_dim=3072 # Standard for gemini-embedding-001
        )
        
        storage_context = StorageContext.from_defaults(vector_store=vector_store)
        
        # Create Index
        index = VectorStoreIndex.from_documents(
            documents, 
            storage_context=storage_context,
            embed_model=self.embed_model
        )
        return index

def get_vector_store(project_id):
    config = getattr(settings, "REMOTE_POSTGRES_CONFIG", {})
    return PGVectorStore.from_params(
        database=config.get("NAME", "postgres"),
        host=config.get("HOST", "localhost"),
        port=config.get("PORT", "5432"),
        user=config.get("USER", "postgres"),
        password=config.get("PASSWORD", ""),
        table_name=f"rag_project_{project_id}",
        embed_dim=3072
    )

