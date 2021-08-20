from psycopg2.pool import ThreadedConnectionPool
from contextlib import contextmanager
from http.server import HTTPServer, BaseHTTPRequestHandler
import random
import threading
import time


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

# Used to randomly select a query.
QUERIES = {
    'users': INSERT_USERS,
    'posts': INSERT_POSTS,
    'comments': INSERT_COMMENTS,
}

# The maximum time between inserts.
MAX_TIME = 5.0


# To simulate switch over to new containers, we'll use a global pools.
pools = {}
current_pool = "src"
pools["src"] = ThreadedConnectionPool(
    minconn=0,
    maxconn=10,
    database="database",
    user="database",
    password="database",
    host="src",
    port=5432,
)
pools["dest"] = ThreadedConnectionPool(
    minconn=0,
    maxconn=10,
    database="database",
    user="database",
    password="database",
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
        yield connection, connection.cursor()
    finally:
        pools[target].putconn(connection)


class switch_handler(BaseHTTPRequestHandler):
    def do_GET(self):
        """
        Swap the current pool.
        """
        global current_pool

        # Make the switch.
        print("Switching to dest")
        current_pool = "dest"

        # Send a response.
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Switching to dest")


def inserter():
    """
    Connect to the database and insert data.
    """
    # Pick a query.
    query = random.choice(list(QUERIES.keys()))

    # Run the query.
    with get_cursor() as result:
        connection, cursor = result
        cursor.execute(QUERIES[query])
        connection.commit()

    # Print the result.
    print('Inserted ', cursor.rowcount, query)


def runner():
    """
    Loop forever and insert data at random intervals.
    """
    while True:
        # Insert data.
        inserter()

        # Wait for the next iteration.
        time.sleep(random.random() * MAX_TIME)


def main():
    """
    Application entry point.
    """
    # Run the inserter in another thread so that the http server can run.
    thread = threading.Thread(target=runner)
    thread.start()

    # Run the http server.
    host = ("0.0.0.0", 80)
    print("Listening on ", *host)
    httpd = HTTPServer(host, switch_handler)
    httpd.serve_forever()


if __name__ == "__main__":
    main()
