CREATE TABLE IF NOT EXISTS {schema}.users (
  id text,
  password text,
  role text DEFAULT 'standard',
  modules text[] DEFAULT array[]::text[]
);
