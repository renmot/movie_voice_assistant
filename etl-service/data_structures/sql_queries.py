movies_query = """
SELECT
   fw.id,
   fw.title,
   fw.description,
   fw.rating,
   fw.type,
   fw.created,
   fw.modified,
   COALESCE (
       json_agg(
           DISTINCT jsonb_build_object(
               'person_role', pfw.role,
               'person_id', p.id,
               'person_name', p.full_name
           )
       ) FILTER (WHERE p.id is not null),
       '[]'
   ) as persons,
   COALESCE (
       json_agg(
           DISTINCT jsonb_build_object(
               'genre_id', g.id,
               'genre_name', g.name
           )
       ) FILTER (WHERE g.id is not null),
       '[]'
   ) as genres
FROM content.film_work fw
LEFT JOIN content.person_film_work pfw ON pfw.film_work_id = fw.id
LEFT JOIN content.person p ON p.id = pfw.person_id
LEFT JOIN content.genre_film_work gfw ON gfw.film_work_id = fw.id
LEFT JOIN content.genre g ON g.id = gfw.genre_id
WHERE fw.modified > %s OR p.modified > %s OR g.modified > %s
GROUP BY fw.id
ORDER BY fw.modified DESC
"""

genres_query = """
SELECT
    g.id as id,
    g.name as name,
    g.description as description,
    g.modified as modified
FROM content.genre g
WHERE g.modified > %s
ORDER BY g.modified DESC
"""

persons_query = """
    SELECT
        p.id as id,
        p.full_name as name,
        p.modified as modified,
        COALESCE (
           json_agg(
               DISTINCT jsonb_build_object(
                   'id', fw.id,
                   'title', fw.title,
                   'imdb_rating', fw.rating
               )
           )
            FILTER (WHERE fw.id is not null),
           '[]'
       ) as films,
        COALESCE(
            array_agg(DISTINCT pfw.role)
            FILTER (WHERE pfw.id is not null),
            '{}'
        ) as roles,
        COALESCE(
            array_agg(DISTINCT fw.id)
            FILTER (WHERE fw.id is not null),
            '{}'
        )::text[] as film_ids
    FROM content.person p
    LEFT JOIN content.person_film_work pfw ON pfw.person_id = p.id
    LEFT JOIN content.film_work fw ON fw.id = pfw.film_work_id
    WHERE p.modified > %s
    GROUP BY p.id
    ORDER BY p.modified
"""


    # SELECT DISTINCT
    #     p.full_name as name
    # FROM content.person p
    # LEFT JOIN content.person_film_work pfw ON pfw.person_id = p.id
    # WHERE pfw.role = 'director'
    # ORDER BY p.full_name

    # SELECT count(*)
    # FROM content.person p
    # LEFT JOIN content.person_film_work pfw ON pfw.person_id = p.id
    # WHERE pfw.role = 'director'