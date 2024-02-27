"""Class with context to connect to Postgres."""
import os
from contextlib import contextmanager

import psycopg2
from psycopg2.extras import DictCursor
from dotenv import load_dotenv

load_dotenv(".env")


@contextmanager
def postgres_conn_context():
    """Context manager to connect Postgres.

    Yields:
        conn: Connection to Postgres.
    """
    connection_config = {
        "dbname": os.environ.get("POSTGRES_DB"),
        "user": os.environ.get("POSTGRES_USER"),
        "password": os.environ.get("POSTGRES_PASSWORD"),
        "host": os.environ.get("DB_HOST"),
        "port": os.environ.get("DB_PORT"),
        "options": "-c search_path=content",
    }

    conn = psycopg2.connect(**connection_config, cursor_factory=DictCursor)
    yield conn

    conn.close()
