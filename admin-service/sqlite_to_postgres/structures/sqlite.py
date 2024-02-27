from dataclasses import dataclass, field
from datetime import datetime


@dataclass(frozen=True)
class Filmwork:
    id: str
    title: str
    description: str
    creation_date: datetime
    rating: float = field(default=0.0)
    type: str
    file_path: str
    created_at: datetime = field(default=datetime.now())
    updated_at: datetime = field(default=datetime.now())


@dataclass(frozen=True)
class Genre:
    id: str
    name: str
    description: str
    created_at: datetime = field(default=datetime.now())
    updated_at: datetime = field(default=datetime.now())


@dataclass(frozen=True)
class GenreFilmwork:
    id: str
    film_work_id: str
    genre_id: str
    created_at: datetime = field(default=datetime.now())


@dataclass(frozen=True)
class Person:
    id: str
    full_name: str
    created_at: datetime = field(default=datetime.now())
    updated_at: datetime = field(default=datetime.now())


@dataclass(frozen=True)
class PersonFilmwork:
    id: str
    film_work_id: str
    person_id: str
    role: str
    created_at: datetime = field(default=datetime.now())
