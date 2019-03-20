CREATE MATERIALIZED VIEW 
IF NOT EXISTS {schema}.shape_colors
AS
SELECT 
  members.postal_code as id,
  CASE
    WHEN residents IS NOT NULL THEN residents
    ELSE 0
  END AS residents,
  CASE
    WHEN 
      residents IS NOT NULL 
      AND ln(max_residents) - ln(min_residents) > 0 
      THEN LEAST(
        256-(256*(
        (ln(residents)-ln(min_residents))/
        (ln(max_residents)-ln(min_residents)))),
        256
      )
    ELSE 256
  END as red,
  CASE
    WHEN events IS NOT NULL THEN events
    ELSE 0
  END as events,
  CASE
    WHEN 
      events IS NOT NULL 
      AND ln(max_events) - ln(min_events) > 0  
      THEN LEAST(
        256-(256*(
        (ln(events)-ln(min_events))/
        (ln(max_events)-ln(min_events)))),
        256
      )
    ELSE 256 
  END as blue
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
          AND postal_code <> '{zip_code}'
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
