"""Starts ETL process to load data from postgres to elasticsearch."""

from time import sleep

from config import settings
from etl.film import ETLFilm


if __name__ == "__main__":
    while True:
        etl_film = ETLFilm()
        for batch in etl_film.extract():
            data = etl_film.transform(batch)
            etl_film.load(data)
        sleep(settings.update_time)

