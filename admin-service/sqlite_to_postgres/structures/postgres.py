import uuid
from dataclasses import dataclass, field
from datetime import datetime


@dataclass(frozen=True)
class Filmwork:
    title: str
    description: str
    creation_date: datetime
    type: str
    file_path: str
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    rating: float = field(default=0.0)
    created: datetime = field(default=datetime.now())
    modified: datetime = field(default=datetime.now())


@dataclass(frozen=True)
class Genre:
    name: str
    description: str
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    created: datetime = field(default=datetime.now())
    modified: datetime = field(default=datetime.now())


@dataclass(frozen=True)
class GenreFilmwork:
    genre_id: uuid.UUID
    film_work_id: uuid.UUID
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    created: datetime = field(default=datetime.now())


@dataclass(frozen=True)
class Person:
    full_name: str
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    created: datetime = field(default=datetime.now())
    modified: datetime = field(default=datetime.now())


@dataclass(frozen=True)
class PersonFilmwork:
    film_work_id: uuid.UUID
    person_id: uuid.UUID
    role: str
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    created: datetime = field(default=datetime.now())


table_dataclass = {
    "content.film_work": Filmwork,
    "content.genre": Genre,
    "content.genre_film_work": GenreFilmwork,
    "content.person": Person,
    "content.person_film_work": PersonFilmwork,
}
