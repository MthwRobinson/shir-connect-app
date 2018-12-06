CREATE MATERIALIZED VIEW 
IF NOT EXISTS {schema}.event_aggregates
AS
SELECT 
  a.id as id,
  capacity,
  changed,
  created,
  description,
  start_datetime,
  end_datetime,
  EXTRACT(isodow FROM start_datetime) AS day_of_week,
  end_datetime - start_datetime as duration,
  is_free,
  a.name as name,
  status,
  url,
  vanity_url,
  venue_id,
  load_datetime,
  address_1,
  address_2,
  city,
  region,
  country,
  latitude,
  longitude,
  postal_code,
  b.name as venue_name,
  c.total_fees,
  c.attendee_count
FROM {schema}.events a
LEFT JOIN {schema}.venues b
ON a.venue_id = b.id
LEFT JOIN(
  SELECT 
    event_id, 
    SUM(cost) AS total_fees,
    COUNT(*) AS attendee_count
  FROM {schema}.attendees
  GROUP BY event_id
) c ON a.id=c.event_id
ORDER BY start_datetime desc
WITH DATA;

CREATE INDEX IF NOT EXISTS event_aggregate_index 
ON {schema}.event_aggregates (start_datetime);


