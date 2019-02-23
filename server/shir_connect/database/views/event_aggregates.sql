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
  c.attendee_count,
  CASE
    WHEN (lower(description) like '% meal %'
      OR lower(description) like '% breakfast %'
      OR lower(description) like '% lunch %'
      OR lower(description) like '% dinner %'
      OR lower(a.name) like '% meal %'
      OR lower(a.name) like '% breakfast %'
      OR lower(a.name) like '% lunch %'
      OR lower(a.name) like '% dinner %'
    ) THEN TRUE
    ELSE FALSE
  END as is_food
FROM {schema}.events a
LEFT JOIN {schema}.venues b
ON a.venue_id = b.id
LEFT JOIN(
  SELECT 
    event_id, 
    SUM(cost) AS total_fees,
    COUNT(*) AS attendee_count
  FROM (
    SELECT DISTINCT 
      event_id,
      max(cost) as cost,
      lower(first_name),
      lower(last_name)
    FROM {schema}.attendees
    GROUP BY lower(first_name), lower(last_name), event_id
  ) x
  GROUP BY event_id
) c ON a.id=c.event_id
ORDER BY start_datetime desc
WITH DATA;

CREATE INDEX IF NOT EXISTS event_aggregate_index 
ON {schema}.event_aggregates (start_datetime);


