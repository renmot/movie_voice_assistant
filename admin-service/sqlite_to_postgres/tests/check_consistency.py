import datetime

from db_connections.sqlite import sqlite_conn_context
from db_connections.postgres import postgres_conn_context
from settings import settings
from structures.common import postgres_col, tables


def test_rows_count():
    """The number of rows is the same."""
    with sqlite_conn_context() as sqlite_conn, postgres_conn_context() as pg_conn:
        sqlite_curs = sqlite_conn.cursor()
        pg_curs = pg_conn.cursor()
        for table in tables:
            sqlite_curs.execute(f"SELECT COUNT(*) AS count FROM {table.sqlite}")
            sqlite_length = int(dict(sqlite_curs.fetchone()).get("count"))

            pg_curs.execute(f"SELECT COUNT(*) FROM {table.postgres}")
            postgres_length = int(pg_curs.fetchone()[0])

            assert sqlite_length == postgres_length


def test_rows_values():
    """Values check."""
    with sqlite_conn_context() as sqlite_conn, postgres_conn_context() as pg_conn:
        sqlite_curs = sqlite_conn.cursor()
        pg_curs = pg_conn.cursor()
        for table in tables:
            sqlite_curs.execute(f"PRAGMA table_info({table.sqlite})")
            sqlite_columns = tuple(
                dict(sqlite_row).get("name") for sqlite_row in sqlite_curs.fetchall()
            )

            pg_columns = tuple(
                postgres_col(sqlite_column) for sqlite_column in sqlite_columns
            )
            pg_columns_str = ", ".join(pg_columns)

            sqlite_curs.execute(f"SELECT * FROM {table.sqlite}")
            while True:
                sqlite_chunk = sqlite_curs.fetchmany(settings.chunk_size)
                if not sqlite_chunk:
                    break

                for sqlite_row in sqlite_chunk:
                    sqlite_dict = dict(sqlite_row)
                    pg_curs.execute(
                        f"SELECT {pg_columns_str} FROM {table.postgres} WHERE id='{sqlite_dict.get('id')}'"  # noqa: E501
                    )
                    pg_row = pg_curs.fetchone()
                    assert pg_row

                    for pg_column_id, _ in enumerate(pg_columns):
                        if type(pg_row[pg_column_id]) is datetime.datetime:
                            pg_datetime = pg_row[pg_column_id].strftime(
                                "%Y-%m-%d %H:%M:%S"
                            )
                            sqlite_datetime = sqlite_dict.get(
                                sqlite_columns[pg_column_id]
                            ).split(".")[0]

                            assert pg_datetime == sqlite_datetime
                        else:
                            assert pg_row[pg_column_id] == sqlite_dict.get(
                                sqlite_columns[pg_column_id]
                            )
