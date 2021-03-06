#!/bin/bash
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" <<- EOSQL
CREATE TABLE users(
  id    SERIAL PRIMARY KEY,
  email VARCHAR(40) NOT NULL
);
CREATE TABLE posts(
  id      SERIAL PRIMARY KEY,
  user_id INTEGER NOT NULL REFERENCES users(id),
  title   VARCHAR(100) NOT NULL
);
CREATE TABLE comments(
  id      SERIAL PRIMARY KEY,
  user_id INTEGER NOT NULL REFERENCES users(id),
  post_id INTEGER NOT NULL REFERENCES posts(id),
  body    VARCHAR(500) NOT NULL
);
EOSQL
