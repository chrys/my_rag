# 01-May 
let's do some housekeeping. The aim is to have fewer high level directories and for the code to be all under `/src/`
Some changes: 
1. Do we need .cache? If not remove it. 
2. Move `/apps/` under  `/src/`
3. Move `/my_rag_project/` under  `/src/apps/`

Then test that nothing broke after making the above moves 

# 01-May2B
- I want to use llamaindex for the RAG projects. 
- llamaindex should do the indexing when a file is uploaded for RAG projects. 
- Embeddings should be created using the gemini embedding model gemini-embedding-001
- llamaindex should be used during for the retrieval. The flow is the following: 
    - User clicks on tab Chat
    - User types a query for the chatbot and clicks Enter or button Send
    - llamaindex should be used for the query 