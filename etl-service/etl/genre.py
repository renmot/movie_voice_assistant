import logging.config
from datetime import datetime

from config import LOGGING_CONFIG
from loaders.genre import ElasticSearchLoader, PostgresExtractor
from data_structures.sql_queries import genres_query
from state import RedisStorage, State
from data_structures.tables import ElasticSearchGenreDetailed

logging.config.dictConfig(LOGGING_CONFIG)


class ETLGenre:
    """A class for ETL data from Postgres to Elasticsearch.
    When the application is restarted, it continues to work from the stop
    location fixed in state.
    States can be stored in Redis or json's file.
    """

    def __init__(self):
        """Connects to databases."""
        self.state = State(RedisStorage())
        # self.state = State(JsonFileStorage('genre_states.json'))
        self.postgres = PostgresExtractor()
        self.elastic = ElasticSearchLoader()

    def extract(self) -> list[dict]:
        """Extract data from Postgres starting from the date in state 'modified'."""
        logging.info("Starting EXTRACT")
        state = self.state.get_state("genre_modified")
        modified = state or datetime.min
        for batch in self.postgres.extract_genres(genres_query, (modified,)):
            yield batch
        logging.info("EXTRACT is finished")

    def transform(self, batch: list[dict]) -> list[ElasticSearchGenreDetailed]:
        """Transform data for elasticsearch using pydantic class.
        Args:
            batch: batch of data from postgres base
        Return:
            list of transforming data
        """
        logging.info("Starting TRANSFORM")
        data = []
        for row in batch:
            transformed_row = ElasticSearchGenreDetailed(
                genre_id=row["id"],
                genre_name=row["name"],
                genre_description=row["description"],
                modified=row["modified"],
            )
            data.append(transformed_row)
        logging.info("TRANSFORM is finished")
        return data

    def load(self, data):
        """Loads data to Elasticsearch index. Sets new state."""
        logging.info("Starting LOAD")
        state = self.elastic.load_data(data)
        self.state.set_state("genre_modified", state)
        logging.info("LOAD is finished")
