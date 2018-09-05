CREATE TABLE IF NOT EXISTS {schema}.venues (
  id text,
  address_1 text,
  address_2 text,
  city text,
  region text,
  country text,
  latitude numeric,
  longitude numeric,
  postal_code text,
  name text
);

--CREATE UNIQUE INDEX IF NOT EXISTS venue_index ON {schema}.venues (id);
