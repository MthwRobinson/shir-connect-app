CREATE MATERIALIZED VIEW 
IF NOT EXISTS {schema}.shape_colors
AS
SELECT 
  members.postal_code as id,
  residents,
  256-(256*((residents-min_residents)/(max_residents-min_residents))) as red,
  events,
  256-(256*((events-min_events)/(max_events-min_events))) as blue
FROM(
  SELECT
    postal_code,
    residents,
    (
      SELECT MAX(residents) 
      FROM(
        SELECT 
        CAST(COUNT(*) AS DECIMAL
        ) as residents 
        FROM {schema}.members_view 
        WHERE postal_code IS NOT NULL
        GROUP BY postal_code
      ) x
    ) as max_residents,
    (
      SELECT MIN(residents) 
      FROM(
        SELECT 
        CAST(COUNT(*) AS DECIMAL) as residents 
        FROM {schema}.members
        WHERE postal_code IS NOT NULL
        GROUP BY postal_code
      ) x
     ) as min_residents
    FROM(
      SELECT 
        CAST(COUNT(*) AS DECIMAL) as residents,
        postal_code
      FROM {schema}.members
      WHERE postal_code IS NOT NULL
      GROUP BY postal_code
    ) a
  ) members
  LEFT JOIN (
    SELECT
      postal_code,
      events,
      (
        SELECT MAX(events) 
        FROM(
          SELECT 
            CAST(COUNT(*) AS DECIMAL) as events 
          FROM {schema}.event_aggregates
          WHERE postal_code IS NOT NULL
          GROUP BY postal_code
        ) x
      ) as max_events,
      (
        SELECT MIN(events) 
        FROM(
          SELECT 
            CAST(COUNT(*) AS DECIMAL) as events 
          FROM {schema}.event_aggregates
          WHERE postal_code IS NOT NULL
          GROUP BY postal_code
        ) x
      ) as min_events
    FROM(
      SELECT 
        CAST(COUNT(*) AS DECIMAL) as events,
        postal_code
      FROM {schema}.event_aggregates
      WHERE postal_code IS NOT NULL
      GROUP BY postal_code
    ) a
) events
ON events.postal_code = members.postal_code
WITH DATA
