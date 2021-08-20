from psycopg2.pool import ThreadedConnectionPool
from contextlib import contextmanager
from http.server import HTTPServer, BaseHTTPRequestHandler
import random


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

# To simulate switch over to new containers, we'll use a global pools.
pools = {}
current_pool = "src"
pools["src"] = ThreadedConnectionPool(
    minconn=0,
    maxconn=10,
    database="src",
    user="src",
    password="src",
    host="src",
    port=5432,
)
pools["dest"] = ThreadedConnectionPool(
    minconn=0,
    maxconn=10,
    database="dest",
    user="dest",
    password="dest",
    host="dest",
    port=5432,
)


@contextmanager
def get_cursor():
    """
    Get a cursor from the current pool.
    """
    global pools
    global current_pool

    # Copy the pool in case it changes.
    target = current_pool[:]

    connection = pools[target].getconn()
    try:
        yield connection.cursor()
    finally:
        pools[target].putconn(connection)


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        """
        Swap the current pool.
        """
        global current_pool

        # Make the switch.
        print("switching to dest")
        current_pool = "dest"

        # Send a response.
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"switching to dest")


def main():
    """
    Application entry point.
    """
    # Create the server.
    host = ("0.0.0.0", 80)
    print("Listening on %s:%d" % host)
    httpd = HTTPServer(host, SimpleHTTPRequestHandler)
    httpd.serve_forever()


if __name__ == "__main__":
    main()
