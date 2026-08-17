"""Server-only database connection helpers."""

from .config import settings


def server_database_url() -> str:
    return settings.supabase_db_url or settings.database_url


def connect():
    import psycopg

    url = server_database_url()
    if not url:
        raise RuntimeError("server database is not configured")
    return psycopg.connect(url)

