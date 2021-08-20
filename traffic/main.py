import psycopg2


INSERT_USERS = """
INSERT INTO users(email)
SELECT
  'user_' || (random() * 1000000)::int || '@' || (
    CASE (random() * 2)::int
      WHEN 0 THEN 'gmail'
      WHEN 1 THEN 'hotmail'
      WHEN 2 THEN 'yahoo'
    END
  ) || '.com' AS email
FROM generate_series(1, (random() * 10)::int) seq
"""

INSERT_POSTS = """
INSERT INTO posts(user_id, title)
WITH expanded AS (
  SELECT
  random()
  ,seq
  ,u.id AS user_id
  FROM generate_series(1, (random() * 50)::int) seq
  JOIN users u ON true
), shuffled AS (
  SELECT e.*
  FROM expanded e
  JOIN (
    SELECT
      ei.seq
      ,min(ei.random)
    FROM expanded ei
    GROUP BY ei.seq
  ) em ON (
    e.seq = em.seq
    AND e.random = em.min
  )
  ORDER BY e.seq
)
SELECT
  s.user_id,
  'It is ' || s.seq || ' ' || (
    CASE (random() * 2)::INT
      WHEN 0 THEN 'sql'
      WHEN 1 THEN 'elixir'
      WHEN 2 THEN 'ruby'
    END
  ) as title
FROM shuffled s
"""

INSERT_COMMENTS = """
INSERT INTO comments(user_id, post_id, body)
WITH expanded AS (
  SELECT
    random()
    ,seq
    ,u.id AS user_id
    ,p.id AS post_id
  FROM generate_series(1, (random() * 200)::int) seq
  JOIN users u ON true
  JOIN posts p ON true
), shuffled AS (
  SELECT e.*
  FROM expanded e
  JOIN (
    SELECT
      ei.seq
      ,min(ei.random)
    FROM expanded ei
    GROUP BY ei.seq
  ) em ON (
    e.seq = em.seq
    AND e.random = em.min
  )
  ORDER BY e.seq
)
SELECT
  s.user_id,
  s.post_id,
  'Here is a number: ' || s.seq AS body
FROM shuffled s
"""

# To simulate switch over to new containers, we'll use a global object to
# store the connection parameters.
parameters = {
    "user": "src",
    "password": "src",
    "host": "src",
    "port": "5432",
    "database": "src",
}

with psycopg2.connect(**parameters) as connection:
    with connection.cursor() as cursor:
        cursor.execute("SELECT 1")

print("all done")
