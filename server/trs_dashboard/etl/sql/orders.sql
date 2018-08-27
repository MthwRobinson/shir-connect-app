CREATE TABLE IF NOT EXISTS {schema}.orders (
  id text,
  changed timestamp,
  cost numeric,
  created timestamp,
  email text,
  first_name text,
  last_name text,
  name text,
  status text
);

CREATE UNIQUE INDEX IF NOT EXISTS attendee_index ON {schema}.orders (id);
