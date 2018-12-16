CREATE MATERIALIZED VIEW 
IF NOT EXISTS {schema}.participants
AS
SELECT DISTINCT 
    CASE 
      WHEN a.first_name IS NOT NULL THEN INITCAP(a.first_name)
      ELSE INITCAP(b.first_name)
    END AS first_name,
    CASE 
      WHEN a.last_name IS NOT NULL THEN INITCAP(a.last_name)
      ELSE INITCAP(b.last_name)
    END AS last_name,
    CASE 
      WHEN b.first_name IS NOT NULL THEN TRUE
      ELSE FALSE
    END AS is_member,
    e.last_event_date,
    e.event_name,
    e.events_attended
  FROM {schema}.attendees a
  FULL JOIN {schema}.members b
  ON (LOWER(a.first_name) = LOWER(b.first_name)
  AND LOWER(a.last_name) = LOWER(b.last_name))
  LEFT JOIN (
    SELECT DISTINCT
      x.first_name,
      x.last_name,
      event_name,
      x.last_event_date,
      x.events_attended
    FROM(
      SELECT
        MAX(c.start_datetime) last_event_date,
        COUNT(DISTINCT c.name) as events_attended,
        LOWER(d.first_name) AS first_name,
        LOWER(d.last_name) AS last_name
      FROM {schema}.events c
      INNER JOIN {schema}.attendees d
      ON c.id = d.event_id
      GROUP BY LOWER(d.first_name), LOWER(d.last_name)
    ) x
    INNER JOIN (
      SELECT
        c.start_datetime last_event_date,
        c.name AS event_name,
        LOWER(d.first_name) AS first_name,
        LOWER(d.last_name) AS last_name
      FROM {schema}.events c
      INNER JOIN {schema}.attendees d
      ON c.id = d.event_id
    ) y
    ON (x.first_name=y.first_name AND x.last_name=y.last_name
    AND x.last_event_date=y.last_event_date)
  ) e
  ON (LOWER(a.first_name) = LOWER(e.first_name)
  AND LOWER(a.last_name) = LOWER(e.last_name))                 
WITH DATA
