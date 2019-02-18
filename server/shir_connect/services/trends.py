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
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
import pandas as pd

from shir_connect.database.database import Database
import shir_connect.configuration as conf
from shir_connect.services.utils import demo_mode, validate_inputs

trends = Blueprint('trends', __name__)

EVENT_TABLE = """
    SELECT DISTINCT
        event_id,
        c.name as event_name,
        b.id as member_id,
        INITCAP(a.name) as member_name,
        a.id as attendee_id,
        concat(
            date_part('year', start_datetime),
            '-', date_part('month', start_datetime)
        ) as event_month,
        date_part('year', start_datetime) as event_year,
        date_part('year', start_datetime) - date_part('year', birth_date) as age
    FROM {schema}.attendees a
    INNER JOIN {schema}.members_view b
    ON (LOWER(a.first_name)=LOWER(b.first_name) 
    AND LOWER(a.last_name)=LOWER(b.last_name))
    INNER JOIN {schema}.event_aggregates c
    ON a.event_id = c.id
"""

@trends.route('/service/trends/authorize', methods=['GET'])
@jwt_required
def member_authorize():
    """ Checks to see if the user is authorized to see members """
    database = Database()
    jwt_user = get_jwt_identity()
    user = database.get_item('users', jwt_user)
    if conf.TRENDS_GROUP not in user['modules']:
        response = {'message': '%s does not have access to trends'%(jwt_user)}
        return jsonify(response), 403
    else:
        del user['password']
        return jsonify(user), 200

@trends.route('/service/trends/monthly-revenue', methods=['GET'])
@jwt_required
def month_revenue():
    """ Finds event revenue aggregated by month """
    trends = Trends()
    # Make sure user has access to the trends page
    jwt_user = get_jwt_identity()
    user = trends.database.get_item('users', jwt_user)
    if conf.TRENDS_GROUP not in user['modules']:
        response = {'message': '%s does not have access to members'%(jwt_user)}
        return jsonify(response), 403
    response = trends.get_monthly_revenue()
    return jsonify(response)

@trends.route('/service/trends/avg-attendance', methods=['GET'])
@jwt_required
def average_attendance():
    """ Finds the avg event attendace by day of week """
    trends = Trends()
    # Make sure user has access to the trends page
    jwt_user = get_jwt_identity()
    user = trends.database.get_item('users', jwt_user)
    if conf.TRENDS_GROUP not in user['modules']:
        response = {'message': '%s does not have access to members'%(jwt_user)}
        return jsonify(response), 403
    response = trends.get_average_attendance()
    return jsonify(response)

@trends.route('/service/trends/age-group-attendance', methods=['GET'])
@jwt_required
@validate_inputs(fields={'request.groupBy': {'type': 'str', 'max': 20}})
def age_group_attendees():
    """ Finds a distinct count of attendees by age group and year """
    trends = Trends()
    # Make sure user has access to the trends page
    jwt_user = get_jwt_identity()
    user = trends.database.get_item('users', jwt_user)
    if conf.TRENDS_GROUP not in user['modules']:
        response = {'message': '%s does not have access to members'%(jwt_user)}
        return jsonify(response), 403

    group_by = request.args.get('groupBy')
    if not group_by:
        group_by = 'year'
    response = trends.get_age_group_attendees(group=group_by)
    return jsonify(response)

@trends.route('/service/trends/participation/<age_group>', methods=['GET'])
@jwt_required
@validate_inputs(fields={'request.top': {'type': 'str', 'max': 20}})
def participation(age_group):
    """ Finds the top events or participants by age group """
    trends = Trends()
    # Make sure user has access to the trends page
    jwt_user = get_jwt_identity()
    user = trends.database.get_item('users', jwt_user)
    if conf.TRENDS_GROUP not in user['modules']:
        response = {'message': '%s does not have access to members'%(jwt_user)}
        return jsonify(response), 403

    top = request.args.get('top')
    if not top:
        top = 'member'
    limit = request.args.get('limit')
    if not limit:
        limit = 25
    response = trends.get_participation(age_group, top, limit)
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

    def get_age_group_attendees(self, group='year'):
        """ Returns a count of unique attendees by age group and year """
        if group == 'year':
            group_by = 'event_year'
        elif group == 'month':
            group_by = 'event_month'
        event_table = EVENT_TABLE.format(schema=self.database.schema)
        age_groups = self.build_age_groups()
        sql = """
            SELECT
                {age_groups},
                {group},
                COUNT(DISTINCT member_name) as distinct_attendees
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

    @demo_mode([{'results': ['name']}]) 
    def get_participation(self, age_group, top='member', limit=25):
        """ Pulls the top events or attendees by age group """
        event_table = EVENT_TABLE.format(schema=self.database.schema)
        age_groups = self.build_age_groups()
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
                    member_name,
                    member_id
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

    @staticmethod
    def build_age_groups():
        """ Builds the SQL case statement to determine a 
        participant's age group """
        age_groups = conf.AGE_GROUPS
        sql = ' CASE '
        for group in age_groups:
            # Build the conditions
            conditions = []
            if 'min' in age_groups[group]:
                condition = ' age >= %s '%(age_groups[group]['min'])
                conditions.append(condition)
            if 'max' in age_groups[group]:
                condition = ' age < %s '%(age_groups[group]['max'])
                conditions.append(condition)

            # If there are no conditions, skip thegroup
            if len(conditions) == 0:
                continue
            # Build the SQL statement
            else:
                sql += ' WHEN ' + ' AND '.join(conditions)
                sql += ' THEN ' + " '%s' "%(group)
        sql += " ELSE 'Unknown' END as age_group "
        return sql
