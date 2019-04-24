CREATE TABLE IF NOT EXISTS {schema}.attendee_to_participant (
  id text,
  participant_id text
);

CREATE UNIQUE INDEX IF NOT EXISTS attendee_match_id
ON {schema}.attendee_to_participant (id);
