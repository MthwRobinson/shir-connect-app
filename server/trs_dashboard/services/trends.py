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
