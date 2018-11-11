"""
REST Endpoints for trends
A user must be authenticated to use end points
Includes:
    1. Flask routes with /trends path
    2. Trends class to manage database calls
"""
import datetime
import logging

import daiquiri
from flask import Blueprint, jsonify
from flask_jwt_simple import jwt_required
import pandas as pd

from trs_dashboard.database.database import Database

trends = Blueprint('trends', __name__)

@trends.route('/service/trends/monthly-revenue')
@jwt_required
def month_revenue():
    """ Finds event revenue aggregated by month """
    trends = Trends()
    response = trends.get_monthly_revenue()
    return jsonify(response)

@trends.route('/service/trends/avg-attendance')
@jwt_required
def average_attendance():
    """ Finds the avg event attendace by day of week """
    trends = Trends()
    response = trends.get_average_attendance()
    return jsonify(response)

@trends.route('/service/trends/age-group-attendees')
@jwt_required
def age_group_attendees():
    """ Finds a distinct count of attendees by age group and year """
    trends = Trends()
    response = trends.get_age_group_attendees()
    return jsonify(response)

class Trends(object):
    """ Class that handles database calls for trends """
    def __init__(self):
        daiquiri.setup(level=logging.INFO)
        self.logger = daiquiri.getLogger(__name__)

        self.database = Database()

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

    def get_age_group_attendees(self):
        """ Returns a count of unique attendees by age group and year """
        sql = """
            SELECT
                CASE
                    WHEN age < 13 THEN 'Under 13'
                    WHEN age >= 13 AND age < 18 THEN 'Teens'
                    WHEN age >= 18 AND age < 23 THEN 'College'
                    WHEN age >= 23 AND age < 40 THEN 'Young Professional'
                    WHEN age >= 40 AND age < 50 THEN '40-50'
                    WHEN age >= 50 AND age < 60 THEN '50-60'
                    WHEN age >= 60 AND age < 70 THEN '60-70'
                    WHEN age >= 70 AND age < 80 THEN '70-80'
                    WHEN age >= 80 THEN 'Over 80'
                    ELSE 'Unknown'
                END AS age_group,
                event_year,
                COUNT(DISTINCT attendee_id) as distinct_attendees
            FROM(
                SELECT DISTINCT
                    event_id,
                    b.id as member_id,
                    a.id as attendee_id,
                    date_part('year', start_datetime) as event_year,
                    date_part('year', start_datetime) - date_part('year', birth_date) as age
                FROM {schema}.attendees a
                INNER JOIN {schema}.members_view b
                ON (LOWER(a.first_name)=LOWER(b.first_name) 
                AND LOWER(a.last_name)=LOWER(b.last_name))
                INNER JOIN {schema}.event_aggregates c
                ON a.event_id = c.id
            ) x
            GROUP BY event_year, age_group
            ORDER BY event_year ASC, age_group DESC
        """.format(schema=self.database.schema)
        list_response = self.database.fetch_list(sql)

        response = {}
        for row in list_response['results']:
            age_group = row['age_group']
            if age_group not in response:
                response[age_group] = {'year': [], 'count': []}
            response[age_group]['year'].append(row['event_year'])
            response[age_group]['count'].append(row['distinct_attendees'])
        return response
