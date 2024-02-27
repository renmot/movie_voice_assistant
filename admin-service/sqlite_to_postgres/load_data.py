"""Script for uploading data from SQLite to Postgres."""
from sqlite3 import Connection as SQLiteConnection

from psycopg2.extensions import connection as postgres_connection
from tabulate import tabulate

from db_connections.postgres import postgres_conn_context
from db_connections.sqlite import sqlite_conn_context
from db_controllers.postgres import PostgresController
from db_controllers.sqlite import SQLiteController
from settings.settings import chunk_size
from structures.common import Timer, tables
from utils.logger import logger

timer = Timer()


def show_table_sizes(
    sqlite_connection: SQLiteConnection, pg_connection: postgres_connection
) -> None:
    """Outputting a table with the sizes of SQLite and Postgres tables to the logs

    Parameters:
        pg_connection: Connection to Postgres
        sqlite_connection: Connection to SQLite
    """

    logger.info("Length of tables")
    length_data = []
    timer.start()
    for current_step, table in enumerate(tables):
        sqlite_curs.execute(f"SELECT COUNT(*) AS count FROM {table.sqlite}")
        table.sqlite_length = dict(sqlite_curs.fetchone()).get("count")

        pg_curs.execute(f"SELECT COUNT(*) FROM {table.postgres}")
        table.postgres_length = pg_curs.fetchone()[0]

        length_data.append(
            (
                current_step + 1,
                table.sqlite,
                table.postgres,
                table.sqlite_length,
                table.postgres_length,
                table.sqlite_length == table.postgres_length,
            )
        )

    logger.info(
        "\n"
        + tabulate(
            length_data,
            headers=("#", "SQLite", "Postgres", "SQLite", "Postgres", "Equal"),
        )
    )
    logger.info(f"Length of tables gor for {timer.get_value()}")


if __name__ == "__main__":
    # Work with SQLite and Postgres connection via context managers.
    with sqlite_conn_context() as sqlite_conn, postgres_conn_context() as pg_conn:
        logger.info("Start to copy data from SQLite to Postgres\n")

        sqlite_curs = sqlite_conn.cursor()
        pg_curs = pg_conn.cursor()

        show_table_sizes(pg_conn, sqlite_conn)

        logger.info(f"Copy data from SQLite to Postgres with chunk size = {chunk_size}")
        timer.start()

        sqlite_ctrl = SQLiteController(sqlite_conn)
        pg_ctrl = PostgresController(pg_conn)

        tables_count = len(tables)
        for current_step, table in enumerate(tables):
            logger.info(f"Step {current_step + 1}/{tables_count}.")
            logger.info(
                f"Copy from {table.sqlite}(SQLite) to {table.postgres}(Postgres)"
            )

            sqlite_curs = sqlite_ctrl.extract(table.sqlite)
            copied_rows = 0

            sqlite_chunk = sqlite_curs.fetchmany(chunk_size)
            while sqlite_chunk:
                pg_ctrl.insert(sqlite_chunk, table.postgres)
                copied_rows += len(sqlite_chunk)
                logger.info(f"Copied {copied_rows}/{table.sqlite_length} rows")

                sqlite_chunk = sqlite_curs.fetchmany(chunk_size)

        logger.info(f"Copied all data from SQLite to Postgres for {timer.get_value()}")

    logger.info("All works done")
