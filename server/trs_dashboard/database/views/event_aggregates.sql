CREATE MATERIALIZED VIEW 
IF NOT EXISTS trs_dashboard.event_aggregates
AS
SELECT 
  a.id,
  name,
  EXTRACT(isodow FROM start_datetime) AS day_of_week,
  start_datetime,
  end_datetime,
  end_datetime - start_datetime as duration,
  postal_code,
  b.total_fees,
  attendee_count,
  json_agg(json_build_object(
    'ticket_type', c.ticket_class_name,
    'cost', c.cost,
    'total_fees', c.total_fees,
    'attendees', c.attendees
  )) as ticket_type
FROM trs_dashboard.events a
LEFT JOIN(
  SELECT 
    event_id, 
    SUM(cost) AS total_fees,
    COUNT(*) AS attendee_count
  FROM trs_dashboard.attendees
  GROUP BY event_id
) b ON a.id=b.event_id
LEFT JOIN(
  SELECT
    event_id,
    ticket_class_name,
    COUNT(*) as attendees,
    cost,
    SUM(cost) as total_fees
  FROM trs_dashboard.attendees
  GROUP BY event_id, ticket_class_name, cost
) c ON c.event_id = c.event_id
LEFT JOIN(
  SELECT id, postal_code
  FROM trs_dashboard.venues
) d ON a.venue_id = d.id
GROUP BY 
  a.id,
  name,
  start_datetime,
  end_datetime,
  postal_code,
  b.total_fees,
  attendee_count
ORDER BY start_datetime desc
WITH DATA
