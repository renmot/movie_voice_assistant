settings = {
    "index": {
        "refresh_interval": "1s",
        "number_of_shards": "1",
        "analysis": {
            "filter": {
                "russian_stemmer": {"type": "stemmer", "language": "russian"},
                "english_stemmer": {"type": "stemmer", "language": "english"},
                "english_possessive_stemmer": {
                    "type": "stemmer",
                    "language": "possessive_english",
                },
                "russian_stop": {"type": "stop", "stopwords": "_russian_"},
                "english_stop": {"type": "stop", "stopwords": "_english_"},
            },
            "analyzer": {
                "ru_en": {
                    "filter": [
                        "lowercase",
                        "english_stop",
                        "english_stemmer",
                        "english_possessive_stemmer",
                        "russian_stop",
                        "russian_stemmer",
                    ],
                    "tokenizer": "standard",
                }
            },
        },
    }
}

movies_index = {
    "index": "movie",
    "settings": settings,
    "mappings": {
        "dynamic": "strict",
        "properties": {
            "id": {"type": "keyword"},
            "imdb_rating": {"type": "float"},
            "genre": {"type": "keyword"},
            "genres": {
                "type": "nested",
                "dynamic": "strict",
                "properties": {
                    "id": {"type": "keyword"},
                    "name": {"type": "text", "analyzer": "ru_en"},
                },
            },
            "title": {
                "type": "text",
                "analyzer": "ru_en",
                "fields": {"raw": {"type": "keyword"}},
            },
            "description": {"type": "text", "analyzer": "ru_en"},
            "director": {"type": "text", "analyzer": "ru_en"},
            "actors_names": {"type": "text", "analyzer": "ru_en"},
            "writers_names": {"type": "text", "analyzer": "ru_en"},
            "directors": {
                "type": "nested",
                "dynamic": "strict",
                "properties": {
                    "id": {"type": "keyword"},
                    "name": {"type": "text", "analyzer": "ru_en"},
                },
            },
            "actors": {
                "type": "nested",
                "dynamic": "strict",
                "properties": {
                    "id": {"type": "keyword"},
                    "name": {"type": "text", "analyzer": "ru_en"},
                },
            },
            "writers": {
                "type": "nested",
                "dynamic": "strict",
                "properties": {
                    "id": {"type": "keyword"},
                    "name": {"type": "text", "analyzer": "ru_en"},
                },
            },
            "modified": {"type": "date"},
        },
    },
}

persons_index = {
    "index": "persons",
    "settings": settings,
    "mappings": {
        "dynamic": "strict",
        "properties": {
            "id": {"type": "keyword"},
            "name": {"type": "text", "analyzer": "ru_en"},
            "role": {"type": "keyword"},
            "film_ids": {"type": "keyword"},
        },
    },
}

genres_index = {
    "index": "genres",
    "settings": settings,
    "mappings": {
        "dynamic": "strict",
        "properties": {
            "id": {"type": "keyword"},
            "name": {
                "type": "text",
                "analyzer": "ru_en",
                "fields": {"keyword": {"type": "keyword", "ignore_above": 256}},
            },
            "description": {"type": "text", "analyzer": "ru_en"},
            "film_ids": {"type": "keyword"},
            "modified": {"type": "date"},
        },
    },
}

persons_index = {
    "index": "persons",
    "body": {
        "settings": settings,
        "mappings": {
            "dynamic": "strict",
            "properties": {
                "id": {"type": "keyword"},
                "name": {
                    "type": "text",
                    "analyzer": "ru_en",
                    "fields": {"keyword": {"type": "keyword", "ignore_above": 256}},
                },
                "film_ids": {
                    "type": "text",
                },
                "films": {
                    "type": "nested",
                    "dynamic": "strict",
                    "properties": {
                        "id": {"type": "keyword"},
                        "title": {"type": "text", "analyzer": "ru_en"},
                        "imdb_rating": {"type": "float"},
                    },
                },
                "roles": {"type": "text", "analyzer": "ru_en"},
                "modified": {"type": "date"},
            },
        },
    },
}
