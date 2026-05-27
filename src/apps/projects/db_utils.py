import psycopg2
from django.conf import settings
from logging import getLogger

logger = getLogger(__name__)

def test_postgres_connection() -> tuple[bool, str]:
    """
    Test the connection to the remote PostgreSQL database using REMOTE_POSTGRES_CONFIG.

    Returns
    -------
    tuple[bool, str]
        (success, error_message)
    """
    config = getattr(settings, "REMOTE_POSTGRES_CONFIG", {})
    
    db_name = config.get("NAME")
    db_user = config.get("USER")
    db_pass = config.get("PASSWORD")
    db_host = config.get("HOST")
    db_port = config.get("PORT", "5432")
    
    if not all([db_name, db_user, db_pass, db_host]):
        return False, "Missing remote PostgreSQL connection credentials in environment variables."

    try:
        conn = psycopg2.connect(
            host=db_host,
            port=int(db_port),
            database=db_name,
            user=db_user,
            password=db_pass,
            connect_timeout=5
        )
        conn.close()
        return True, ""
    except Exception as exc:
        logger.error(f"PostgreSQL connection check failed: {exc}")
        return False, str(exc)
