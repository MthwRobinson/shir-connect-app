CREATE TABLE IF NOT EXISTS {schema}.participant_match (
  id text,
  member_id text,
  first_name text,
  last_name text,
  nickname text,
  email text,
  birth_date timestamp,
  is_birth_date_estimated boolean
);

CREATE UNIQUE INDEX IF NOT EXISTS participant_match_id ON {schema}.participant_match (id);
