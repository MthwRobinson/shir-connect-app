CREATE MATERIALIZED VIEW 
IF NOT EXISTS {schema}.participants
AS
SELECT DISTINCT
    a.id as participant_id,
    INITCAP(a.first_name) as first_name,
    INITCAP(a.last_name) as last_name,
    INITCAP(a.fake_first_name) as fake_first_name,
    INITCAP(a.fake_last_name) as fake_last_name,
    CASE 
      WHEN b.active_member IS NULL THEN FALSE
      ELSE b.active_member
    END AS is_member,
    e.first_event_date,
    e.last_event_date,
    e.event_name,
    e.fake_event_name,
    CASE
      WHEN e.events_attended IS NOT NULL THEN e.events_attended
      ELSE 0
    END AS events_attended,
    DATE_PART('year', AGE(now(), a.birth_date)) as age
  FROM {schema}.participant_match a
  LEFT JOIN {schema}.members_view b
  ON a.member_id = b.id
  LEFT JOIN {schema}.attendee_to_participant c
  ON c.participant_id = a.id
  LEFT JOIN {schema}.attendees d
  ON d.id = c.id
  LEFT JOIN (
    SELECT
      x.participant_id,
      event_name,
      fake_event_name,
      x.last_event_date,
      x.first_event_date,
      x.events_attended
    FROM(
      SELECT
        MAX(events.start_datetime) AS last_event_date,
        MIN(events.start_datetime) AS first_event_date,
        COUNT(DISTINCT events.id) AS events_attended,
        MAX(events.name) as event_name,
        MAX(events.fake_name) as fake_event_name,
        participant_id
      FROM {schema}.events events
      INNER JOIN {schema}.attendees attendees
      ON attendees.event_id = events.id
      INNER JOIN {schema}.attendee_to_participant participants
      ON participants.id = attendees.id
      GROUP BY participant_id
    ) x
    INNER JOIN (
      SELECT
        events.start_datetime last_event_date,
        participant_id
      FROM {schema}.events events
      INNER JOIN {schema}.attendees attendees
      ON attendees.event_id = events.id
      INNER JOIN {schema}.attendee_to_participant participants
      ON participants.id = attendees.id
    ) y
    ON x.participant_id = y.participant_id
    AND y.last_event_date = x.last_event_date
  ) e
ON e.participant_id = c.participant_id
WITH DATA
