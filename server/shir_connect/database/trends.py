""" Services for pulling trend data from the database. """
import logging

import daiquiri

import shir_connect.configuration as conf
from shir_connect.database.database import Database
from shir_connect.database.utils import build_age_groups

class Trends:
    """ Class that handles database calls for trends """
    def __init__(self, database=None):
        daiquiri.setup(level=logging.INFO)
        self.logger = daiquiri.getLogger(__name__)

        self.database = database if database else Database()

    def get_monthly_revenue(self):
        """ Returns revenue aggregated by month """
        sql = """
            SELECT
                CASE
                    WHEN SUM(total_fees) IS NOT NULL
                        THEN SUM(total_fees)
                    ELSE NULL
                END AS revenue,
                EXTRACT(MONTH FROM start_datetime) as mn,
                EXTRACT(YEAR FROM start_datetime) as yr
            FROM {schema}.event_aggregates
            GROUP BY yr, mn
            ORDER BY yr ASC, mn ASC
        """.format(schema=self.database.schema)
        response = self.database.fetch_list(sql)
        return response

    def get_average_attendance(self):
        """ Returns average attendance by weekday """
        sql = """
            SELECT
                AVG(attendee_count) as avg_attendance,
                CASE
                    WHEN day_of_week = 0 THEN 'Sunday'
                    WHEN day_of_week = 1 THEN 'Monday'
                    WHEN day_of_week = 2 THEN 'Tuesday'
                    WHEN day_of_week = 3 THEN 'Wednesday'
                    WHEN day_of_week = 4 THEN 'Thursday'
                    WHEN day_of_week = 5 THEN 'Friday'
                    WHEN day_of_week = 7 THEN 'Saturday'
                END AS day_of_week,
                day_of_week as day_order
            FROM(
                SELECT
                    attendee_count,
                    EXTRACT(dow FROM start_datetime) AS day_of_week
                FROM {schema}.event_aggregates
                WHERE attendee_count > 0
            ) x
            GROUP BY day_of_week
            ORDER BY day_order ASC
        """.format(schema=self.database.schema)
        response = self.database.fetch_list(sql)
        return response

    def get_age_group_attendees(self, group='year'):
        """ Returns a count of unique attendees by age group and year """
        if group == 'year':
            group_by = 'event_year'
        elif group == 'month':
            group_by = 'event_month'
        event_table = EVENT_TABLE.format(schema=self.database.schema)
        age_groups = build_age_groups()
        sql = """
            SELECT
                {age_groups},
                {group},
                COUNT(DISTINCT participant_id) as distinct_attendees
            FROM( {event_table} ) x
            GROUP BY {group}, age_group
            ORDER BY {group} ASC, age_group DESC
        """.format(
            age_groups=age_groups,
            event_table=event_table,
            group=group_by
        )
        list_response = self.database.fetch_list(sql)

        response = {}
        for row in list_response['results']:
            age_group = row['age_group']
            if age_group not in response:
                response[age_group] = {'group': [], 'count': []}
            response[age_group]['group'].append(row[group_by])
            response[age_group]['count'].append(row['distinct_attendees'])
        return response

    def get_participation(self, age_group, top='participant', limit=25):
        """ Pulls the top events or attendees by age group """
        event_table = EVENT_TABLE.format(schema=self.database.schema)
        age_groups = build_age_groups()
        sql = """
            SELECT
                count(*) as total,
                {top}_name as name,
                {top}_id as id
            FROM (
                SELECT DISTINCT
                    {age_groups},
                    event_name,
                    event_id,
                    participant_name,
                    participant_id
                FROM( {event_table} ) x
            ) y
            WHERE age_group='{age_group}'
            GROUP BY age_group, {top}_name, {top}_id
            ORDER BY total DESC
            LIMIT {limit}
        """.format(
            age_groups=age_groups,
            top=top,
            event_table=event_table,
            age_group=age_group,
            limit=limit
        )
        response = self.database.fetch_list(sql)
        return response

EVENT_TABLE = """
    SELECT DISTINCT
        event_id,
        d.participant_id,
        c.name as event_name,
        CONCAT(INITCAP(a.first_name), ' ',
               INITCAP(a.last_name)) as participant_name,
        a.id as attendee_id,
        concat(
            date_part('year', start_datetime),
            '-', date_part('month', start_datetime)
        ) as event_month,
        date_part('year', start_datetime) as event_year,
        age
    FROM {schema}.attendees a
    INNER JOIN {schema}.attendee_to_participant b
    ON b.id = a.id
    INNER JOIN {schema}.participants d
    ON d.participant_id = b.participant_id
    INNER JOIN {schema}.event_aggregates c
    ON a.event_id = c.id
"""
