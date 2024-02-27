"""Controller for Postgres."""
from dataclasses import fields

from psycopg2.extensions import connection as postgres_connection
from psycopg2.extensions import cursor as postgres_cursor

from structures.common import sqlite_col
from structures.postgres import table_dataclass


class PostgresController:
    """Controller for Postgres."""

    conn: postgres_connection
    curs: postgres_cursor

    def __init__(self, connection: postgres_connection) -> None:
        """Get cursror from the connection.

        Prameters:
            connection: Coneection for Postgres.
        """
        self.conn = connection
        self.curs = connection.cursor()

    def insert(self, sqlite_chunk: tuple, table_name: str) -> None:
        """Data saving to the table.

        Parameters:
            sqlite_chunk: Set of data from the SQLite
            table_name: Table name.
        """
        pg_dataclass_fields = tuple(
            field.name for field in fields(table_dataclass[table_name])
        )

        sqlite_columns = []
        pg_columns = []

        sqlite_keys = dict(sqlite_chunk[0]).keys()
        for pg_column in pg_dataclass_fields:
            sqlite_column = sqlite_col(pg_column)
            if sqlite_column in sqlite_keys:
                sqlite_columns.append(sqlite_column)
                pg_columns.append(pg_column)

        data_template = "(" + ",".join("%s" for _ in pg_columns) + "), "
        query = f'INSERT INTO {table_name} ({", ".join(pg_columns)}) VALUES '

        data = []
        for sqlite_row in sqlite_chunk:
            query += data_template
            for sqlite_column in sqlite_columns:
                data.append(dict(sqlite_row).get(sqlite_column))
        query = query[:-2]
        query += " ON CONFLICT(id) DO NOTHING"

        self.curs.execute(query, data)
        self.conn.commit()
