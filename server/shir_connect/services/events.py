"""
REST Endpoints for events
A user must be authenticated to use end points
Includes:
    1. Flask routes with /event/<event_id> paths
    2. Flask routes with /events path
    3. Events class to manage database calls
"""
import csv
import datetime
from io import StringIO
import json
import logging

import daiquiri
from flask import Blueprint, abort, jsonify, make_response, request
from flask_jwt_extended import jwt_required, get_jwt_identity
import pandas as pd
import numpy as np

from shir_connect.database.database import Database
import shir_connect.configuration as conf
from shir_connect.services.utils import demo_mode, validate_inputs

events = Blueprint('events', __name__)

@events.route('/service/event/<event_id>', methods=['GET'])
@jwt_required
@validate_inputs(fields={'event_id': {'type': 'int'}})
def get_event(event_id):
    """ Pulls the information for an event from the database """
    event_manager = Events()
    # Make sure the user has access to the module
    jwt_user = get_jwt_identity()
    user = event_manager.database.get_item('users', jwt_user)
    if conf.EVENT_GROUP not in user['modules']:
        response = {'message': '%s does not have acccess to events'%(jwt_user)}
        return jsonify(response), 403

    event = event_manager.get_event(event_id)
    if event:
        return jsonify(event)
    else:
        response = {'message': 'not found'}
        return jsonify(response), 404

@events.route('/service/events', methods=['GET'])
@jwt_required
@validate_inputs(fields={'start_date': {'type': 'date'},
                         'end_date': {'type': 'date'}})
def get_events():
    """ Pulls events from the database """
    event_manager = Events()
    # Make sure the user has access to the module
    jwt_user = get_jwt_identity()
    user = event_manager.database.get_item('users', jwt_user)
    if conf.EVENT_GROUP not in user['modules']:
        response = {'message': '%s does not have acccess to events'%(jwt_user)}
        return jsonify(response), 403

    limit = request.args.get('limit')
    if not limit:
        limit = 25
    else:
        limit = int(limit)
    page = request.args.get('page')
    if not page:
        page = 1
    else:
        page = int(page)
    order = request.args.get('order')
    if not order:
        order = 'desc'
    sort = request.args.get('sort')
    if not sort:
        sort = 'start_datetime'

    where = []
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    if start_date or end_date:
        conditions = {}
        if start_date:
            conditions['>='] = "'{}'".format(start_date)
        if end_date:
            conditions['<'] = "'{}'".format(end_date)
        where.append(('start_datetime', conditions))

    q = request.args.get('q')

    response = event_manager.get_events(
        limit=limit,
        page=page,
        order=order,
        sort=sort,
        q=q,
        where=where
    )
    return jsonify(response)

@events.route('/service/events/locations', methods=['GET'])
@jwt_required
def get_event_locations():
    """ Pulls the most recent event at each location """
    event_manager = Events()
    # Make sure the user has access to the module
    jwt_user = get_jwt_identity()
    user = event_manager.database.get_item('users', jwt_user)
    if conf.MAP_GROUP not in user['modules']:
        response = {'message': '%s does not have acccess to the map'%(jwt_user)}
        return jsonify(response), 403
    response = event_manager.get_event_locations()
    return jsonify(response)

@events.route('/service/events/cities', methods=['GET'])
@jwt_required
def get_event_cities():
    """ Pulls a list of events grouped by city """
    event_manager = Events()
    # Make sure the user has access to the module
    jwt_user = get_jwt_identity()
    user = event_manager.database.get_item('users', jwt_user)
    if conf.MAP_GROUP not in user['modules']:
        response = {'message': '%s does not have acccess to the map'%(jwt_user)}
        return jsonify(response), 403
    response = event_manager.get_event_cities()
    return jsonify(response)

@events.route('/service/events/export', methods=['GET'])
@jwt_required
def export_event_aggregates():
    """ Exports the event aggregates as a csv """
    database = Database()
    # Make sure the user has access to the module
    jwt_user = get_jwt_identity()
    user = database.get_item('users', jwt_user)
    if conf.EVENT_GROUP not in user['modules']:
        response = {'message': '%s does not have acccess to events'%(jwt_user)}
        return jsonify(response), 403

    q = request.args.get('q')
    if q:
        query = ('name', q)
    else:
        query = None

    database = Database()
    df = database.read_table('event_aggregates', query=query)
    today = str(datetime.datetime.now())[:10]
    filename = 'event_aggregates_%s.csv'%(today)

    buffer = StringIO()
    df.to_csv(buffer, encoding='utf-8', index=False)
    output = make_response(buffer.getvalue())
    output.headers["Content-Disposition"] = "attachment; filename=export.csv"
    output.headers["Content-type"] = "text/csv"
    return output
    
class Events(object):
    """ Class that handles event database calls """
    def __init__(self):
        daiquiri.setup(level=logging.INFO)
        self.logger = daiquiri.getLogger(__name__)

        self.database = Database()
   
    @demo_mode([{'results': ['name', 'venue_name']}])
    def get_events(self, limit=None, page=None, order=None, 
                   sort=None, q=None, where=[]):
        """ Fetches the most recent events from the database """
        if q:
            query = ('name', q)
        else:
            query = None
        df = self.database.read_table(
            'event_aggregates',
            limit=limit,
            page=page,
            order=order,
            sort=sort,
            query=query,
            where=where
        )
        count = self.database.count_rows('event_aggregates', query=query,
                                         where=where)

        pages = int((count/limit)) + 1
        events = self.database.to_json(df)
        response = {'results': events, 'count': str(count), 'pages': pages}
        return response

    @demo_mode([
        'address_1',
        'address_2',
        'city',
        'country',
        'description',
        'name',
        'region',
        'venue_name',
        'postal_code',
        {'attendees': ['email', 'first_name', 'last_name', 'name']}
    ])
    def get_event(self, event_id):
        """ Returns an event from the database """
        event = self.database.get_item('event_aggregates', event_id)
        if event:
            # Peform type conversions on the columns
            col_to_string = [
                'duration', 
                'start_datetime', 
                'end_datetime'
            ] 
            for column in event.keys():
                if type(event[column]) == int:
                    col_to_string.append(column)
                elif isinstance(event[column], np.int64):
                    col_to_string.append(column)
                elif event[column] in [True, False]:
                    col_to_string.append(column)
                if column in col_to_string:
                    event[column] = str(event[column])

            # Add attendees and event aggregate information
            event['attendees'] = self.get_attendees(event_id)
            event = self.compute_aggregates(event)

        return event

    def compute_aggregates(self, event):
        """ Computes event aggregates for the event quick facts view """
        # Compute the aggregate statistics
        start_date = str(event['start_datetime'])[:10]
        total_age = 0
        age_count = 0
        members = 0
        first_event_count = 0
        age_groups = {}
        for attendee in event['attendees']:
            # Compile age group information
            age_group_found = False 
            if attendee['age']:
                # Updates for the average age
                total_age += attendee['age']
                age_count += 1

                # Update the age group count
                for group in conf.AGE_GROUPS:
                    meets_reqs = True
                    conditions = conf.AGE_GROUPS[group]
                    if 'min' in conditions:
                        if attendee['age'] < conditions['min']:
                            meets_reqs = False
                    if 'max' in conditions:
                        if attendee['age'] >= conditions['max']:
                            meets_reqs = False
                    if meets_reqs:
                        age_group_found = True
                        if group not in age_groups:
                            age_groups[group] = 1
                        else:
                            age_groups[group] += 1

            # Add to the unknown category, if necessary
            if not age_group_found:
                if 'Unknown' not in age_groups:
                    age_groups['Unknown'] = 1
                else:
                    age_groups['Unknown'] += 1
            
            # See if the participant is a member
            if attendee['is_member']:
                members += 1

            # Check to see if the participant is a first
            # time participants
            if not attendee['first_event_date']:
                first_event_count += 1
            else:
                first_event_date = str(attendee['first_event_date'])[:10]
                if first_event_date == start_date:
                    first_event_count += 1

        # Add age/age group information to the event
        if total_age > 0:
            average_age = total_age/age_count
        else:
            average_age = False
        event['average_age'] = average_age
        event['age_groups'] = age_groups

        # Add member breakdown to the event
        event['member_count'] = members
        event['non_member_count'] = len(event['attendees']) - members

        # Add the number of first timers
        event['first_event_count'] = first_event_count

        return event

    def get_attendees(self, event_id):
        """ Pulls the list of the attendees for the event """
        sql = """
            SELECT
                first_name,
                last_name,
                max(age) as age,
                CASE
                    WHEN max(is_member) = 1 THEN TRUE
                    ELSE FALSE
                end as is_member,
                max(first_event_date) as first_event_date,
                max(events_attended) as events_attended
            FROM(
                SELECT DISTINCT
                    INITCAP(a.first_name) as first_name,
                    INITCAP(a.last_name) as last_name,
                    DATE_PART('year', AGE(now(), birth_date)) as age,
                    CASE 
                        WHEN c.first_name IS NOT NULL THEN 1
                        ELSE 0
                    END as is_member,
                    d.first_event_date,
                    d.events_attended
                FROM {schema}.attendees a
                INNER JOIN {schema}.events b
                on a.event_id = b.id
                LEFT JOIN {schema}.members_view c
                ON (lower(a.first_name)=lower(c.first_name)
                AND lower(a.last_name)=lower(c.last_name))
                LEFT JOIN {schema}.participants d
                ON (lower(a.first_name)=lower(d.first_name)
                AND lower(a.last_name)=lower(d.last_name))
                where b.id = '{event_id}'
            ) x
            GROUP BY first_name, last_name
            ORDER BY last_name ASC
        """.format(schema=self.database.schema, event_id=event_id)
        df = pd.read_sql(sql, self.database.connection)
        attendees = self.database.to_json(df)

        # Conver the first_event_date epoch time to a timestamp
        for attendee in attendees:
            if attendee['first_event_date']:
                first = attendee['first_event_date']
                first_ts = datetime.datetime.fromtimestamp(first/1000)
                attendee['first_event_date'] = first_ts.isoformat()
        return attendees

    def get_event_cities(self):
        """ Pulls a list of events organized by city """
        sql = """
            SELECT
                event.id as event_id,
                event.name as event_name,
                venue.city as city
            FROM {schema}.events event
            INNER JOIN {schema}.venues venue
            ON event.venue_id = venue.id
        """.format(schema=self.database.schema)
        df = pd.read_sql(sql, self.database.connection)

        cities = {}
        counts = {}
        total = 0
        for i in df.index:
            row = dict(df.loc[i])
            city = row['city']
            if city:
                if row['city'] not in cities:
                    cities[city] = [row]
                    counts[city] = 1
                else:
                    cities[city].append(row)
                    counts[city] += 1
                total += 1
        counts = {x: str(counts[x]) for x in counts}
        
        response = {
            'results': {
                'cities': cities,
                'counts': counts
            },
            'count': str(total)
        }
        return response

    def get_event_locations(self):
        """ Pulls the latest event at each latitude/longitude """
        sql = """
            SELECT 
                events.event_id as event_id,
                events.start_datetime,
                event_name,
                address_1,
                city,
                events.latitude,
                events.longitude
            FROM(
                SELECT 
                    max(a.id) as event_id,
                    max(start_datetime)
                    latitude,
                    longitude
                FROM {schema}.events a
                INNER JOIN {schema}.venues b
                ON a.venue_id = b.id
                GROUP BY latitude, longitude
            ) max_location
            INNER JOIN (
                SELECT 
                    a.id as event_id,
                    start_datetime,
                    a.name as event_name,
                    address_1,
                    city,
                    latitude,
                    longitude
                FROM {schema}.events a
                INNER JOIN {schema}.venues b
                ON a.venue_id = b.id
            ) events
            ON max_location.event_id = events.event_id
        """.format(schema=self.database.schema)
        df = pd.read_sql(sql, self.database.connection)

        features = []
        for i in df.index:
            row = dict(df.loc[i])
            feature = self.build_feature(row)
            features.append(feature)
        response = {'results': features, 'count': len(features)}
        return response

    def build_feature(self, row):
        """ Converts a dataframe row into a geojson feature """
        # Mask the event name and address if the app is in dev mode
        if conf.DEMO_MODE:
            row['event_name'] = 'EVENT_NAME'
            row['address_1'] = 'ADDRESS'
            row['city'] = 'CITY'

        coordinates = [row['longitude'], row['latitude']]
        day = str(row['start_datetime'])[:10]
        address = ''
        if row['address_1']:
            address += row['address_1'] + ', '
        if row['city']:
            address += row['city']
        description = """
            <strong>{title}</strong>
            <ul>
                <li>Date: {day}</li>
                <li>Address: {address}</li>
            </ul>
        """.format(title=row['event_name'], day=day, address=address)

        feature = {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": coordinates
            },
            "properties": {
                "title": row['event_name'],
                "icon": 'marker',
                "description": description
            }
        }
        return feature
