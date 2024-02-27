import contextlib
import logging.config

import psycopg2
from elasticsearch import Elasticsearch, helpers
from psycopg2.extras import DictCursor

from backoff import backoff
from config import LOGGING_CONFIG, settings
from data_structures.indices import movies_index
from data_structures.tables import ElasticSearchSchemaFilm

logging.config.dictConfig(LOGGING_CONFIG)


class PostgresExtractor:
    """Extracts data from Postgres."""

    @backoff(logging=logging)
    def extract_movies(self, select_query: str, params: tuple) -> list[dict]:
        """Extract data from filmwork
        Args:
            select_query: string of postgres query for delivery
            params: tuple of special parameters for postgres query
        Yield:
            batch of extracted data
        """
        with contextlib.closing(
            psycopg2.connect(**settings.postgres_dsn.dict(), cursor_factory=DictCursor)
        ) as self.conn, self.conn.cursor() as self.cursor:
            logging.info("Postgres DB connected")
            select_query = self.cursor.mogrify(select_query, params)
            self.cursor.execute(select_query)
            while batch := self.cursor.fetchmany(settings.batch_size):
                yield batch


class ElasticSearchLoader:
    """Loads data to Elasticsearch."""

    @backoff(logging=logging)
    def __init__(self) -> None:
        """Initialize elasticsearch loader. Check the availability of desired index"""
        self.client = Elasticsearch(**settings.elastic_dsn.dict())
        logging.info("ElasticSearch DB connected")
        self.check_or_create_index()

    def check_or_create_index(self):
        """Creates the desired index if there is none."""
        if not self.client.indices.exists(index="movie"):
            self.client.indices.create(**movies_index)
            logging.info('Created index "movies" in ElasticSearch DB')

    @backoff(logging=logging)
    def load_data(self, data) -> str:
        """Loads data to elasticsearch's index.
        Return:
            string the biggest 'modified' date for state
        """
        helpers.bulk(self.client, self.gendata(data), stats_only=True)
        modified = self.client.search(
            index="movie",
            body={
                "query": {"match_all": {}},
                "sort": [{"modified": {"order": "desc"}}],
                "size": 1,
            },
        )["hits"]["hits"][0]["_source"]["modified"]
        return modified

    @staticmethod
    def gendata(data: list[ElasticSearchSchemaFilm]):
        """Generates structure of the index documents."""
        for row in data:
            yield {"_index": "movie", "_id": row.id, "_source": row.json()}
