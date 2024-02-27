import abc
import json
import logging
from typing import Any

from redis import Redis, exceptions

from backoff import backoff
from config import LOGGING_CONFIG, settings

logging.config.dictConfig(LOGGING_CONFIG)


class BaseStorage:
    @abc.abstractmethod
    def save_state(self, state: dict) -> None:
        """Save state to persistent storage"""
        pass

    @abc.abstractmethod
    def retrieve_state(self) -> dict:
        """Load state locally from persistent storage"""
        pass


class JsonFileStorage(BaseStorage):
    def __init__(self, file_path: str | None = None):
        self.file_path = file_path

    def save_state(self, state: dict) -> None:
        with open(self.file_path, "w") as outfile:
            json.dump(state, outfile)

    def retrieve_state(self) -> dict:
        try:
            with open(self.file_path, "r") as json_file:
                data = json.load(json_file)
        except FileNotFoundError:
            data = {}
        return data or {}


class RedisStorage(BaseStorage):
    def __init__(self):
        self.db = None
        self.connect()

    @backoff(logging=logging)
    def connect(self):
        self.db = Redis(**settings.redis_dsn_.model_dump())
        logging.info("Redis DB connected")

    @backoff(logging=logging)
    def save_state(self, state: dict) -> None:
        try:
            self.db.mset(state)
        except exceptions.ConnectionError:
            logging.error("Error connecting to the Redis DB")
            self.connect()
            self.db.mset(state)

    @backoff(logging=logging)
    def retrieve_state(self) -> dict:
        try:
            self.db.ping()
        except exceptions.ConnectionError:
            logging.error("Error connecting to the Redis DB")
            self.connect()
        return self.db


class State:
    """A class for storing state when working with data."""

    def __init__(self, storage: BaseStorage):
        self.storage = storage

    def set_state(self, key: str, value: Any) -> None:
        """Set the state for a specific key."""
        self.storage.save_state(state={key: value})

    def get_state(self, key: str) -> Any:
        """Get the state by a specific key."""
        return self.storage.retrieve_state().get(key)
