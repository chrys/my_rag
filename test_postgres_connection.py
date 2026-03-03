#!/usr/bin/env python3
"""
Manual Postgres connectivity test script
Tests each layer of the connection to diagnose timeout issues
"""

import os
import sys
import time
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def print_section(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")

def test_env_vars():
    """Check if environment variables are set"""
    print_section("1. Environment Variables")
    
    env_vars = {
        'DB_HOST': os.getenv('DB_HOST'),
        'DB_PORT': os.getenv('DB_PORT', '5432'),
        'DB_NAME': os.getenv('DB_NAME'),
        'DB_USER': os.getenv('DB_USER'),
        'DB_PASSWORD': '***' if os.getenv('DB_PASSWORD') else 'NOT SET',
    }
    
    for key, value in env_vars.items():
        status = "✓" if value and value != '***' else "✗"
        print(f"{status} {key}: {value}")
    
    missing = [k for k, v in env_vars.items() if not v or v == 'NOT SET']
    return len(missing) == 0, missing

def test_network_connectivity():
    """Test basic network connectivity to the DB host"""
    print_section("2. Network Connectivity")
    
    db_host = os.getenv('DB_HOST')
    db_port = os.getenv('DB_PORT', '5432')
    
    if not db_host:
        print("✗ DB_HOST not set, skipping network test")
        return False
    
    try:
        import socket
        print(f"Testing connection to {db_host}:{db_port}...")
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)  # 5 second timeout for socket
        result = sock.connect_ex((db_host, int(db_port)))
        sock.close()
        
        if result == 0:
            print(f"✓ Network connection successful to {db_host}:{db_port}")
            return True
        else:
            print(f"✗ Network connection failed (error code: {result})")
            print(f"  - Check if {db_host} is reachable")
            print(f"  - Check if port {db_port} is open")
            print(f"  - Check firewall rules")
            return False
    except socket.gaierror:
        print(f"✗ Hostname resolution failed for {db_host}")
        print("  - Check if DB_HOST is correct")
        print("  - Check DNS resolution")
        return False
    except Exception as e:
        print(f"✗ Network test failed: {e}")
        return False

def test_psycopg_import():
    """Test if psycopg2 (postgres driver) is installed"""
    print_section("3. PostgreSQL Driver (psycopg2)")
    
    try:
        import psycopg2
        print(f"✓ psycopg2 is installed (version: {psycopg2.__version__})")
        return True
    except ImportError:
        print("✗ psycopg2 is NOT installed")
        print("  Install it with: pip install psycopg2-binary")
        return False

def test_basic_pg_connection():
    """Test basic PostgreSQL connection using psycopg2"""
    print_section("4. PostgreSQL Connection (psycopg2)")
    
    try:
        import psycopg2
    except ImportError:
        print("✗ psycopg2 not available, skipping")
        return False
    
    db_host = os.getenv('DB_HOST')
    db_port = os.getenv('DB_PORT', '5432')
    db_name = os.getenv('DB_NAME')
    db_user = os.getenv('DB_USER')
    db_pass = os.getenv('DB_PASSWORD')
    
    if not all([db_host, db_name, db_user, db_pass]):
        print("✗ Missing database credentials")
        return False
    
    try:
        print(f"Connecting to postgresql://{db_user}@{db_host}:{db_port}/{db_name}")
        start_time = time.time()
        
        conn = psycopg2.connect(
            host=db_host,
            port=int(db_port),
            database=db_name,
            user=db_user,
            password=db_pass,
            connect_timeout=10
        )
        elapsed = time.time() - start_time
        
        cur = conn.cursor()
        cur.execute("SELECT version();")
        version = cur.fetchone()[0]
        cur.close()
        conn.close()
        
        print(f"✓ PostgreSQL connection successful ({elapsed:.2f}s)")
        print(f"  Database: {version}")
        return True
        
    except psycopg2.OperationalError as e:
        elapsed = time.time() - start_time
        print(f"✗ Connection failed ({elapsed:.2f}s): {e}")
        print("  Common causes:")
        print("    - Wrong credentials (DB_USER, DB_PASSWORD)")
        print("    - Database doesn't exist (DB_NAME)")
        print("    - Host/port unreachable")
        return False
    except Exception as e:
        print(f"✗ Connection error: {e}")
        return False

def test_sqlalchemy_connection():
    """Test connection using SQLAlchemy (used by txtai)"""
    print_section("5. SQLAlchemy Connection")
    
    try:
        from sqlalchemy import create_engine, text
    except ImportError:
        print("✗ SQLAlchemy not available, skipping")
        return False
    
    db_host = os.getenv('DB_HOST')
    db_port = os.getenv('DB_PORT', '5432')
    db_name = os.getenv('DB_NAME')
    db_user = os.getenv('DB_USER')
    db_pass = os.getenv('DB_PASSWORD')
    
    if not all([db_host, db_name, db_user, db_pass]):
        print("✗ Missing database credentials")
        return False
    
    try:
        connection_string = f"postgresql://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}"
        print(f"Creating engine with: {connection_string.split('@')[0]}@...")
        
        start_time = time.time()
        engine = create_engine(
            connection_string,
            connect_args={"connect_timeout": 10},
            echo=False
        )
        
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version();"))
            version = result.fetchone()[0]
        
        elapsed = time.time() - start_time
        print(f"✓ SQLAlchemy connection successful ({elapsed:.2f}s)")
        return True
        
    except Exception as e:
        elapsed = time.time() - start_time
        print(f"✗ SQLAlchemy connection failed ({elapsed:.2f}s): {e}")
        return False

def test_txtai_connection():
    """Test txtai connection to postgres"""
    print_section("6. txtai PostgreSQL Connection")
    
    try:
        from txtai.embeddings import Embeddings
    except ImportError:
        print("✗ txtai not available")
        return False
    
    db_host = os.getenv('DB_HOST')
    db_port = os.getenv('DB_PORT', '5432')
    db_name = os.getenv('DB_NAME')
    db_user = os.getenv('DB_USER')
    db_pass = os.getenv('DB_PASSWORD')
    
    if not all([db_host, db_name, db_user, db_pass]):
        print("✗ Missing database credentials")
        return False
    
    try:
        content_url = f"postgresql://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}"
        print(f"Initializing txtai with postgres backend...")
        print(f"Using: {content_url.split('@')[0]}@...")
        
        start_time = time.time()
        embeddings = Embeddings({
            "path": "sentence-transformers/nli-mpnet-base-v2",
            "content": content_url
        })
        elapsed = time.time() - start_time
        
        print(f"✓ txtai initialization successful ({elapsed:.2f}s)")
        print(f"  Note: This initializes the model which may take time on first run")
        return True
        
    except Exception as e:
        elapsed = time.time() - start_time
        print(f"✗ txtai connection failed ({elapsed:.2f}s): {e}")
        print("  This could indicate:")
        print("    - Database connectivity issues")
        print("    - Insufficient timeout for table creation")
        print("    - Missing pgvector extension (if using vector storage)")
        return False

def main():
    print("\n" + "="*60)
    print("  PostgreSQL Connectivity Diagnostic Test")
    print("="*60)
    
    results = {}
    
    # Run all tests
    results['env_vars'], missing = test_env_vars()
    if not results['env_vars']:
        print(f"\n⚠️  Missing environment variables: {', '.join(missing)}")
        return
    
    results['network'] = test_network_connectivity()
    results['psycopg'] = test_psycopg_import()
    results['pg_conn'] = test_basic_pg_connection()
    results['sqlalchemy'] = test_sqlalchemy_connection()
    results['txtai'] = test_txtai_connection()
    
    # Summary
    print_section("Summary")
    
    print("\nTest Results:")
    for name, passed in results.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"  {status}: {name.replace('_', ' ').title()}")
    
    all_passed = all(results.values())
    
    if all_passed:
        print("\n✓ All tests passed! Your PostgreSQL connection is working.")
    else:
        print("\n✗ Some tests failed. Review the output above for details.")
        print("\nCommon timeout causes:")
        print("  1. Network firewall blocking port 5432")
        print("  2. Database server not running or unreachable")
        print("  3. Incorrect credentials")
        print("  4. Slow initial model download (for txtai)")
        print("  5. Connection pool exhaustion on large uploads")
    
    print("\n" + "="*60 + "\n")

if __name__ == '__main__':
    main()
