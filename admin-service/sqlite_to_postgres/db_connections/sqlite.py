"""Class with context to connect to SQLite."""
import os
import sqlite3
from contextlib import contextmanager

from dotenv import load_dotenv

load_dotenv(".env")
db_path = os.environ.get("SQLITE_DB_PATH")


@contextmanager
def sqlite_conn_context():
    """Context manager to connect to SQLite.

    Yields:
        conn: Connection to SQLite.
    """
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    yield conn

    conn.close()
