BEGIN;
  SELECT setval('users_id_seq', 10000);
  SELECT setval('posts_id_seq', 10000);
  SELECT setval('comments_id_seq', 10000);
COMMIT;
