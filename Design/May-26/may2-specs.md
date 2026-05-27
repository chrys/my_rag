1 Postgres DB for local projects
I want local postgres RAG projects to use the VPS postgres DB. The details to connect can be found in .env file, section 
#remote postgres
postgres_name
postgres_user
postgres_password
postgres_host
postgres_port

System should test connectivity and return an error message to the screen when there is no postgres connection.
