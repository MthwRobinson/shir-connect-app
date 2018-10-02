"""
REST Endpoints for events
A user must be authenticated to use end points
Includes:
    1. Flask routes with /event/<event_id> paths
    2. Flask routes with /events path
    3. Events class to manage database calls
"""
import json
import logging

import daiquiri
from flask import Blueprint, abort, jsonify, request
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
            query =None

        df = self.database.read_table(
            'event_aggregates', 
            limit=limit,
            page=page,
            order=order,
            sort=sort,
            query=query
        )
        count = self.database.count_rows('event_aggregates', query=query)

        pages = int((count/limit)) + 1
        events = [json.loads(df.loc[i].to_json()) for i in df.index]
        response = {'results': events, 'count': str(count), 'pages': pages}
        return response

