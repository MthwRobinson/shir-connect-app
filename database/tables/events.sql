CREATE TABLE IF NOT EXISTS {schema}.events (
  id text, 
  capacity integer,
  changed timestamp,
  created timestamp,
  currency text,
  description text,
  end_datetime timestamp,
  is_free boolean,
  name text,
  organization_id text,
  organizer_id text,
  start_datetime timestamp,
  status text,
  fake_name text,
  fake_description text,
  url text,
  vanity_url text,
  venue_id text,
  load_datetime text
);

CREATE UNIQUE INDEX IF NOT EXISTS event_index ON {schema}.events (id);
