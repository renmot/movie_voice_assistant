import datetime
from dataclasses import dataclass, field


@dataclass
class TablePair:
    sqlite: str
    postgres: str
    postgres_columns: tuple
    sqlite_length: int = field(default=None)
    postgres_length: int = field(default=None)


tables = (
    TablePair(
        sqlite="film_work",
        postgres="content.film_work",
        postgres_columns=(
            "id",
            "title",
            "description",
            "creation_date",
            "rating",
            "type",
            "created",
            "modified",
            "file_path",
        ),
    ),
    TablePair(
        sqlite="genre",
        postgres="content.genre",
        postgres_columns=("id", "name", "description", "created", "modified"),
    ),
    TablePair(
        sqlite="genre_film_work",
        postgres="content.genre_film_work",
        postgres_columns=("id", "genre_id", "film_work_id", "created"),
    ),
    TablePair(
        sqlite="person",
        postgres="content.person",
        postgres_columns=("id", "full_name", "created", "modified"),
    ),
    TablePair(
        sqlite="person_film_work",
        postgres="content.person_film_work",
        postgres_columns=("id", "film_work_id", "person_id", "role", "created"),
    ),
)

postgres_sqlite_columns = {
    "created": "created_at",
    "modified": "updated_at",
}


def sqlite_col(postgres_column_name: str) -> str:
    if postgres_column_name in postgres_sqlite_columns:
        return postgres_sqlite_columns[postgres_column_name]

    return postgres_column_name


sqlite_postgres_columns = {
    "created_at": "created",
    "updated_at": "modified",
}


def postgres_col(sqlite_column_name: str) -> str:
    if sqlite_column_name in sqlite_postgres_columns:
        return sqlite_postgres_columns[sqlite_column_name]

    return sqlite_column_name


class Timer:
    start_time = None

    def start(self):
        self.start_time = datetime.datetime.now()

    def get_value(self):
        return datetime.datetime.now() - self.start_time

    def __init__(self):
        self.start()
