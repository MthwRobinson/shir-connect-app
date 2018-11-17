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
from flask_jwt_simple import jwt_required
import pandas as pd

from trs_dashboard.database.database import Database

events = Blueprint('events', __name__)

@events.route('/service/events', methods=['GET'])
@jwt_required
def get_events():
    """ Pulls events from the database """
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
    q = request.args.get('q')

    event_manager = Events()
    response = event_manager.get_events(
        limit=limit,
        page=page,
        order=order,
        sort=sort,
        q=q
    )
    return jsonify(response)

@events.route('/service/events/locations', methods=['GET'])
@jwt_required
def get_event_locations():
    """ Pulls the most recent event at each location """
    event_manager = Events()
    response = event_manager.get_event_locations()
    return jsonify(response)

@events.route('/service/events/cities', methods=['GET'])
@jwt_required
def get_event_cities():
    """ Pulls a list of events grouped by city """
    event_manager = Events()
    response = event_manager.get_event_cities()
    return jsonify(response)

@events.route('/service/events/export', methods=['GET'])
@jwt_required
def export_event_aggregates():
    """ Exports the event aggregates as a csv """
    q = request.args.get('q')
    if q:
        query = ('name', q)
    else:
        query = None

    database = Database()
    df = database.read_table('event_aggregates', query=query)
    # Delete ticket type because CSV has issues with JSON columns
    del df['ticket_type']

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

    def get_events(self, limit=None, page=None, order=None, sort=None, q=None):
        """ Fetches the most recent events from the database """
        if q:
            query = ('name', q)
        else:
            query = None
        columns = [
            'name', 
            'start_datetime', 
            'end_datetime', 
            'total_fees', 
            'attendee_count'
        ]
        df = self.database.read_table(
            'event_aggregates',
            columns = columns,
            limit=limit,
            page=page,
            order=order,
            sort=sort,
            query=query
        )
        count = self.database.count_rows('event_aggregates', query=query)

        pages = int((count/limit)) + 1
        events = self.database.to_json(df)
        response = {'results': events, 'count': str(count), 'pages': pages}
        return response

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
