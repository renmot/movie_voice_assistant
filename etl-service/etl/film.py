import logging.config
from datetime import datetime

from config import LOGGING_CONFIG
from loaders.film import ElasticSearchLoader, PostgresExtractor
from data_structures.sql_queries import movies_query
from state import RedisStorage, State
from data_structures.tables import ElasticSearchSchemaFilm

logging.config.dictConfig(LOGGING_CONFIG)


def get_names(row: dict, role: str) -> list[str]:
    """Get list of persons names for the role in filmwork."""
    names = []
    for person in row["persons"]:
        if person["person_role"] == role:
            names.append(person["person_name"])
    return names


def get_detailed_persons(row: dict, role: str) -> list[dict]:
    """Get person ids and names for the role in filmwork."""
    detailed_persons = []
    for person in row["persons"]:
        if person["person_role"] == role:
            detailed_persons.append(person)
    return detailed_persons


def get_genres(row: list) -> list[str]:
    """Get list of genres's names."""
    genres = []
    for genre in row:
        genres.append(genre["genre_name"].lower())
    return genres


class ETLFilm:
    """A class for ETL data from Postgres to Elasticsearch.
    When the application is restarted, it continues to work from the stop
    location fixed in state.
    States can be stored in Redis or json's file.
    """

    def __init__(self):
        """Connects to databases."""
        self.state = State(RedisStorage())
        # self.state = State(JsonFileStorage('states.json'))
        self.postgres = PostgresExtractor()
        self.elastic = ElasticSearchLoader()

    def extract(self) -> list[dict]:
        """Extract data from Postgres starting from the date in state 'modified'."""
        logging.info("Starting EXTRACT")
        state = self.state.get_state("film_modified")
        modified = state or datetime.min
        for batch in self.postgres.extract_movies(movies_query, (modified,) * 3):
            yield batch
        logging.info("EXTRACT is finished")

    def transform(self, batch: list[dict]) -> list[ElasticSearchSchemaFilm]:
        """Transform data for elasticsearch using pydantic class.
        Args:
            batch: batch of data from postgres base
        Return:
            list of transforming data
        """
        logging.info("Starting TRANSFORM")
        data = []
        for row in batch:
            transformed_row = ElasticSearchSchemaFilm(
                id=row["id"],
                imdb_rating=row["rating"],
                genre=get_genres(row["genres"]),
                genres=row["genres"],
                title=row["title"],
                description=row["description"],
                director=get_names(row, "director"),
                actors_names=get_names(row, "actor"),
                writers_names=get_names(row, "writer"),
                directors=get_detailed_persons(row, "director"),
                actors=get_detailed_persons(row, "actor"),
                writers=get_detailed_persons(row, "writer"),
                modified=row["modified"],
            )
            data.append(transformed_row)
        logging.info("TRANSFORM is finished")
        return data

    def load(self, data):
        """Loads data to Elasticsearch index. Sets new state."""
        logging.info("Starting LOAD")
        state = self.elastic.load_data(data)
        self.state.set_state("film_modified", state)
        logging.info("LOAD is finished")
