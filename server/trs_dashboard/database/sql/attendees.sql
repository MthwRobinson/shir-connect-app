CREATE TABLE IF NOT EXISTS {schema}.attendees (
  id text,
  cancelled boolean,
  changed timestamp,
  checked_in boolean,
  cost numeric,
  created timestamp,
  delivery_method text,
  event_id text,
  order_id text,
  email text,
  first_name text,
  last_name text,
  name text,
  quantity integer,
  refunded boolean,
  ticket_class_id text,
  ticket_class_name text
);

CREATE UNIQUE INDEX IF NOT EXISTS attendee_index ON {schema}.attendees (id);
