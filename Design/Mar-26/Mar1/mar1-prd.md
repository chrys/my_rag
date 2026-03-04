Topic: Unit tests
1. There are two types of storage types I want to be tested: Google File Search and RAG. Existing Unit tests can be found at `Testing/unit`
2. I would like to create unit tests for the Admin tab (for both types)
2.1 Create a project 
2.2 Delete a project
2.3 Upload a file  
2.4 Delete a file. Ensure that when a file is deleted is deindexed from the embeddings either of Google File Search or postgres.
2.5 Add a custom prompt to a project 
2.6 Edit a custom prompt 
2.7 Ensure that a custom prompt is used

3. I would like to create unit tests for the Chat tab (for both types)
3.1 Chat returns related answers
3.2 Chat does not answer not related answers. You can modify the prompt (2.6) of a test project created in 2.1 to ensure that the Chat will reply only to questions related to the content. 

