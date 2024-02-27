from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class ElasticSearchGenre(BaseModel):
    id: str = Field(alias="genre_id")
    name: str = Field(alias="genre_name")


class ElasticSearchGenreDetailed(ElasticSearchGenre):
    description: Optional[str] = Field(alias="genre_description")
    modified: datetime


class ElasticSearchPerson(BaseModel):
    id: str = Field(alias="person_id")
    name: str = Field(alias="person_name")


class ElasticSearchPersonDetailed(ElasticSearchPerson):
    modified: datetime


class ElasticSearchSchemaFilm(BaseModel):
    id: str
    imdb_rating: Optional[float]
    genres: list[ElasticSearchGenre]
    genre: list[str]
    title: str
    description: Optional[str]
    director: list[str]
    actors_names: list[str]
    writers_names: list[str]
    directors: list[ElasticSearchPerson]
    actors: list[ElasticSearchPerson]
    writers: list[ElasticSearchPerson]
    modified: datetime
