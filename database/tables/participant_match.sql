CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS fuzzystrmatch;
CREATE TABLE IF NOT EXISTS {schema}.participant_match (
  id text,
  member_id text,
  first_name text,
  last_name text,
  nickname text,
  email text,
  fake_first_name text,
  fake_last_name text,
  fake_nickname text,
  fake_email text,
  birth_date timestamp,
  is_birth_date_estimated boolean
);

CREATE UNIQUE INDEX IF NOT EXISTS participant_match_id ON {schema}.participant_match (id);
