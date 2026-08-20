import time
from google import genai
from google.genai import errors as genai_errors
from google.genai import types 
import dotenv
import os
import requests


#read GOOGLE_API_KEY from file .env 
dotenv.load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY")

if not API_KEY:
    print("WARNING: GOOGLE_API_KEY environment variable not set - API functions will fail at runtime")
else:
    os.environ["GOOGLE_API_KEY"] = API_KEY

if API_KEY:
    os.environ["GEMINI_API_KEY"] = API_KEY

client = genai.Client(api_key=API_KEY) if API_KEY else None


class GoogleFileSearchPermissionError(RuntimeError):
    """Raised when the configured Google API credentials cannot access a file search store."""


def _is_permission_error(exc: Exception) -> bool:
    return isinstance(exc, genai_errors.ClientError) and getattr(exc, "code", None) == 403



def create_file_search_store(display_name: str) -> str:
    """
    Creates a new File Search Store on Google Cloud and returns its resource name.

    Args:
        display_name: The human-readable name of the store.

    Returns:
        The resource name of the created store (e.g., 'fileSearchStores/abc-123').
    """
    print(f"Creating Google File Search store for '{display_name}'...")
    if not client:
        raise GoogleFileSearchPermissionError("Google File Search client is not configured (missing GOOGLE_API_KEY).")

    try:
        store = client.file_search_stores.create(
            config={'display_name': display_name}
        )
        print(f"✅ Successfully created store: {store.name}")
        return store.name
    except Exception as e:
        print(f"❌ Failed to create store '{display_name}': {e}")
        if _is_permission_error(e):
            raise GoogleFileSearchPermissionError(
                f"Google File Search permission denied while creating store '{display_name}': {e}"
            ) from e
        raise RuntimeError(f"Failed to create Google File Search store '{display_name}': {e}") from e


def delete_file_search_store(store_id_to_delete: str):
    """
    Deletes a specified File Search Store and all its contents permanently.

    Args:
        store_id_to_delete: The unique resource ID of the store 
                            (e.g., 'fileSearchStores/abc-123').
    """
    
    print(f"⚠️ Attempting to permanently delete store: {store_id_to_delete}...")
    
    try:
        # The .delete method requires the 'name' (the store_id)
        # force=True is required to confirm the removal of all resources
        client.file_search_stores.delete(
            name=store_id_to_delete,
        )
        
        print(f"✅ Successfully deleted store: {store_id_to_delete}")
        
    except Exception as e:
        print(f"❌ Failed to delete store {store_id_to_delete}: {e}")

def add_document_to_store(store_id: str, file_path: str, custom_metadata: list[dict] = None, display_name: str = None) -> str:
    """
    Uploads a document to a specified File Search Store and waits for indexing to complete.

    Args:
        store_id: The unique resource ID of the target store 
                  (e.g., 'fileSearchStores/abc-123').
        file_path: The local path to the document you want to upload.
        custom_metadata: Optional list of up to 20 typed metadata dictionaries
                         (e.g. [{'key': 'dept', 'string_value': 'finance'}]).
        display_name: Optional human-readable display name for the document.
                      Defaults to the file's base name.

    Returns:
        The resource name of the uploaded document if successful, otherwise an empty string.
    """
    
    doc_display_name = display_name or os.path.basename(file_path)
    print(f"Uploading and indexing '{doc_display_name}' into store: {store_id}...")
    
    try:
        config = {'display_name': doc_display_name}
        if custom_metadata:
            # Enforce max 20 entries per document
            config['custom_metadata'] = custom_metadata[:20]

        # The upload_to_file_search_store method initiates the indexing process
        operation = client.file_search_stores.upload_to_file_search_store(
            file=file_path,
            file_search_store_name=store_id,
            config=config
        )
        
        print("   ⌛ Waiting for file indexing to complete (This may take a moment)...")

        # --- Wait for Indexing ---
        # Polling the operation ensures the file is fully indexed before you query
        while not operation.done:
            time.sleep(5)
            operation = client.operations.get(operation)

        # Get the result from the completed operation
        # Workaround: Fetch the document by name from the store
        print("   Verifying upload...")
        pager = client.file_search_stores.documents.list(parent=store_id)
        all_docs = list(pager)
        
        # Find documents with matching display name
        matching_docs = [d for d in all_docs if d.display_name == doc_display_name]
        
        if matching_docs:
            # Get the most recently created one
            newest_doc = max(matching_docs, key=lambda d: d.create_time)
            document_resource_name = newest_doc.name
            print(f"   ✅ Indexing complete! Document Resource Name: {document_resource_name}\n")
            return document_resource_name
        else:
             raise Exception(f"Document {file_name} not found in store after upload.")
        
    except Exception as e:
        print(f"❌ Failed to add document to store: {e}")
        if _is_permission_error(e):
            raise GoogleFileSearchPermissionError(
                f"Google File Search permission denied for store {store_id}. Check that the configured API key can access this store and that the store still exists."
            ) from e
        return ""

def ask_store_question(
    store_id: str, 
    query: str, 
    system_prompt: str = None,
    model: str = "gemini-2.5-flash-lite",
    metadata_filters: str = None
) -> str:
    """
    Asks a question, grounding the answer ONLY in the documents of the specified store.

    Args:
        store_id: The unique resource ID of the target store 
                  (e.g., 'fileSearchStores/abc-123').
        query: The user's question.
        system_prompt: Optional custom system prompt to guide the model's response.
        model: Model identifier (defaults to 'gemini-2.5-flash-lite').
        metadata_filters: Optional filter expression (e.g., 'department == "finance"').

    Returns:
        The model's answer, potentially with citations.
    """
    
    target_model = model or "gemini-2.5-flash-lite"
    
    print(f"Querying store '{store_id}' with model {target_model}...")
    if system_prompt:
        print("Using custom system prompt...")
    
    try:
        # --- 1. Configure the FileSearch Tool ---
        from google.genai import types as genai_types
        
        file_search_kwargs = {
            'file_search_store_names': [store_id]
        }
        if metadata_filters:
            file_search_kwargs['metadata_filter'] = metadata_filters
        
        # Create the file search configuration
        file_search_config = genai_types.FileSearch(**file_search_kwargs)
        
        # Create tool with file_search
        file_search_tool = genai_types.Tool(
            file_search=file_search_config
        )

        # --- 2. Build GenerateContentConfig with system_instruction ---
        config_kwargs = {
            'tools': [file_search_tool]
        }
        
        if system_prompt:
            config_kwargs['system_instruction'] = system_prompt
            print(f"[DEBUG] System instruction set: {system_prompt[:50]}...")

        # --- 3. Generate Content ---
        response = client.models.generate_content(
            model=target_model,
            contents=query,
            config=types.GenerateContentConfig(**config_kwargs)
        )

        # --- 4. Format and Return Response ---
        
        if not response.candidates:
             return "No response candidates returned from model."

        answer_text = response.text
        if answer_text is None:
             # Fallback if text is blocked or empty
             if response.candidates[0].finish_reason:
                  return f"Response blocked or finished early: {response.candidates[0].finish_reason}"
             return "No text response generated."
        
        # Optional: Append citations for verification
        citations = []
        if response.candidates and response.candidates[0].grounding_metadata:
            for chunk in response.candidates[0].grounding_metadata.grounding_chunks:
                # The title is the file's display name set during upload
                if chunk.retrieved_context:
                    citations.append(chunk.retrieved_context.title)
        
        if citations:
            answer_text += "\n\n**Sources:** " + ", ".join(set(citations))

        return answer_text

    except Exception as e:
        import traceback
        traceback.print_exc()
        return f"Error processing query: {e}"
    

def list_documents_in_store(store_id: str):
    """
    Retrieves and prints the list of all documents within a specified File Search Store.

    Args:
        store_id: The unique resource ID of the target store 
                  (e.g., 'fileSearchStores/abc-123').
    """
    
    print(f"Fetching documents for store: {store_id}...")
    
    try:
        # The list method is on the 'documents' resource of the store.
        # It requires the 'parent' argument, which is the store's ID.
        pager = client.file_search_stores.documents.list(parent=store_id)
        
        documents = list(pager)
        
        if not documents:
            print(f"No documents found in store: {store_id}")
            return []

        print(f"\nFound {len(documents)} document(s) in the store:")
        print("=" * 60)

        for doc in documents:
            # doc.name is the full Document Resource Name (used for deletion)
            doc_resource_name = doc.name
            
            # doc.display_name is the human-readable name (used for filtering)
            display_name = doc.display_name
            
            print(f"File Name (for filtering): {display_name}")
            print(f"Document ID (for deletion): {doc_resource_name}")
            print(f"State: {doc.state.name}") # State should be 'ACTIVE'
            print("-" * 60)
        
        return documents
        
        
            
    except Exception as e:
        print(f"❌ Failed to list documents for store {store_id}: {e}")
        return []
 
def delete_document_from_store(document_resource_name: str):
    """
    Deletes a specific document and its indexed embeddings from a File Search Store.
    Uses the REST API directly to delete the document.

    Args:
        document_resource_name: The full resource ID of the document to delete 
                                (e.g., 'fileSearchStores/mysecondfilesearchstore-1m3ju15v7hjz/documents/data2txt-dr72i7yy967c').
    """
    
    print(f"⚠️ Attempting to delete document: {document_resource_name}...")
    
    try:
        # Construct the full API endpoint URL with API key as query parameter
        api_url = f"https://generativelanguage.googleapis.com/v1beta/{document_resource_name}?key={API_KEY}&force=true"
        
        # Set up headers
        headers = {
            "Content-Type": "application/json",
        }
        
        # Make DELETE request
        response = requests.delete(api_url, headers=headers)
        
        # Check for successful response
        if response.status_code == 200:
            print(f"✅ Successfully deleted document: {document_resource_name}")
        elif response.status_code == 404:
            print(f"⚠️ Document not found: {document_resource_name}")
        else:
            # Raise exception for other potential errors
            raise Exception(f"API Error {response.status_code}: {response.text}")
        
    except Exception as e:
        print(f"❌ Failed to delete document {document_resource_name}: {e}")
 
