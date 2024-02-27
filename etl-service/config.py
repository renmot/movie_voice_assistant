# import os

from pydantic import Field  # RedisDsn, PostgresDsn,
from pydantic_settings import BaseSettings  # SettingsConfigDict

import logging

logging.basicConfig(level=logging.DEBUG)

# ENV_DIR = os.path.dirname(os.path.abspath(__file__))


class PostgresSettings(BaseSettings):
    dbname: str = Field(validation_alias="POSTGRES_DB")
    user: str = Field(validation_alias="POSTGRES_USER")
    password: str = Field(validation_alias="POSTGRES_PASSWORD")
    host: str = Field(validation_alias="DB_HOST")
    port: str = Field(validation_alias="DB_PORT")
    options: str = "-c search_path=content"

    # class Config:
    #     env_file = ".env"
    #     env_file_encoding = "utf-8"

    # class Config: #remove
    #     env_file = os.path.join(ENV_DIR, ".env")
    #     # env_nested_delimiter = "__"
    #     env_file_encoding = "utf-8"

    # model_config = SettingsConfigDict(
    #     case_sensitive=False,
    #     env_file='.env',
    #     env_file_encoding='utf-8'
    # )


class ElasticSettings(BaseSettings):
    hosts: str = Field(validation_alias="ES_DSN")


#     class Config:
#         env_file = ".env"
#         env_file_encoding = "utf-8"


class RedisSettings(BaseSettings):
    host: str = Field(validation_alias="REDIS_HOST")
    port: int = Field(validation_alias="REDIS_PORT")
    decode_responses: bool = True


#     class Config:
#         env_file = ".env"
#         env_file_encoding = "utf-8"


class Settings(BaseSettings):
    batch_size: int = 100
    update_time: int = 10
    postgres_dsn: PostgresSettings = PostgresSettings()
    elastic_dsn: ElasticSettings = ElasticSettings()
    redis_dsn_: RedisSettings = RedisSettings()
    # redis_dsn: RedisDsn = Field(validation_alias="REDIS_DSN")


logging.debug(PostgresSettings())
logging.debug(ElasticSettings())
logging.debug(RedisSettings())

settings = Settings()

logging.debug(Settings())

LOGGING_CONFIG = {
    "version": 1,
    "root": {"handlers": ["default", "file"], "level": "INFO"},
    "formatters": {
        "standard": {
            "format": "[%(asctime)s] %(levelname)s - %(message)s [%(pathname)s.%(funcName)s:%(lineno)d]",  # noqa
            "datefmt": "%d/%m/%Y %H:%M:%S",
        },
    },
    "handlers": {
        "default": {
            "formatter": "standard",
            "class": "logging.StreamHandler",
        },
        "file": {
            "class": "logging.FileHandler",
            "formatter": "standard",
            "filename": "etl.log",
        },
    },
}
