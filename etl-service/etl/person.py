import logging.config
from datetime import datetime

from config import LOGGING_CONFIG
from loaders.person import ElasticSearchLoader, PostgresExtractor
from data_structures.sql_queries import persons_query
from state import RedisStorage, State
from data_structures.tables import ElasticSearchPersonDetailed

logging.config.dictConfig(LOGGING_CONFIG)


class ETLPerson:
    """A class for ETL data from Postgres to Elasticsearch.
    When the application is restarted, it continues to work from the stop
    location fixed in state.
    States can be stored in Redis or json's file.
    """

    def __init__(self):
        """Connects to databases."""
        self.state = State(RedisStorage())
        # self.state = State(JsonFileStorage('persons_states.json'))
        self.postgres = PostgresExtractor()
        self.elastic = ElasticSearchLoader()

    def extract(self) -> list[dict]:
        """Extract data from Postgres starting from the date in state 'modified'."""
        logging.info("Starting EXTRACT")
        state = self.state.get_state("person_modified")
        modified = state or datetime.min
        for batch in self.postgres.extract_persons(persons_query, (modified,)):
            yield batch
        logging.info("EXTRACT is finished")

    def transform(self, batch: list[dict]) -> list[ElasticSearchPersonDetailed]:
        """Transform data for elasticsearch using pydantic class.
        Args:
            batch: batch of data from postgres base
        Return:
            list of transforming data
        """
        logging.info("Starting TRANSFORM")
        data = []
        for row in batch:
            transformed_row = ElasticSearchPersonDetailed(
                person_id=row["id"],
                person_name=row["name"],
                # film_ids=get_film_ids(row['film_ids']),
                modified=row["modified"],
            )
            data.append(transformed_row)
        logging.info("TRANSFORM is finished")
        return data

    def load(self, data):
        """Loads data to Elasticsearch index. Sets new state."""
        logging.info("Starting LOAD")
        state = self.elastic.load_data(data)
        self.state.set_state("person_modified", state)
        logging.info("LOAD is finished")
