"""Controller for SQLite."""
from sqlite3 import Connection, Cursor


class SQLiteController:
    """Controller class for SQLite."""

    conn: Connection
    curs: Cursor

    def __init__(self, connection: Connection) -> None:
        """Get cursor from the connection.

        Parameters:
            connection: Connection for SQLite.
        """
        self.conn = connection
        self.curs = connection.cursor()

    def extract(self, table_name: str) -> Cursor:
        """Data extraction from the table.

        Parameters:
            table_name: Table name.

        Returns:
            Cursor for reading extracted data.
        """
        self.curs.execute(f"SELECT * FROM {table_name}")
        return self.curs
