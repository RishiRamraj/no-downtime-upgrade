SELECT
  CASE
    WHEN n.nspname = 'public' THEN ''
    ELSE n.nspname || '.'
  END || c.relname AS name
  ,nextval(
    CASE
      WHEN n.nspname = 'public' THEN ''
      ELSE n.nspname || '.'
    END || c.relname
  ) AS value
FROM pg_class c
JOIN pg_namespace n on n.oid = c.relnamespace
JOIN pg_sequence s on c.oid = s.seqrelid
WHERE c.relkind = 'S'
