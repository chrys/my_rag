import os
import json
import psycopg2
import dotenv
dotenv.load_dotenv()

project_id = "postgres_20260602_150448_65261_test_rag_0092e3"
db_name = os.getenv('postgres_name', 'rag_dashboard')
db_user = os.getenv('postgres_user', 'rag_user2')
db_pass = os.getenv('postgres_password', 'ThinkRAG2026!')
db_host = os.getenv('postgres_host', 'localhost')
db_port = os.getenv('postgres_port', '5432')

print(f"Connecting to {db_host}:{db_port}/{db_name} as {db_user}")

conn = psycopg2.connect(
    host=db_host,
    port=int(db_port),
    database=db_name,
    user=db_user,
    password=db_pass
)
cursor = conn.cursor()

# We can query all tables ending with the project ID
cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_name LIKE %s;", (f"%{project_id}",))
tables = [r[0] for r in cursor.fetchall()]
print(f"Found tables: {tables}")

for table in tables:
    try:
        cursor.execute(f"SELECT COUNT(*) FROM {table};")
        cnt = cursor.fetchone()[0]
        print(f"Table: {table} has {cnt} rows.")
        
        # Check column names
        cursor.execute(f"SELECT column_name FROM information_schema.columns WHERE table_name = '{table}';")
        cols = [r[0] for r in cursor.fetchall()]
        print(f"Columns: {cols}")
        
        # Select first 5 metadata values
        metadata_col = "metadata_" if "metadata_" in cols else "metadata"
        cursor.execute(f"SELECT text, {metadata_col} FROM {table} LIMIT 5;")
        rows = cursor.fetchall()
        for idx, row in enumerate(rows):
            print(f"Row {idx+1}: text='{row[0][:120]}...', metadata={row[1]}")
            
    except Exception as e:
        print(f"Error for table {table}: {e}")
        conn.rollback()

cursor.close()
conn.close()
