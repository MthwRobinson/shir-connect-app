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
    
    event_manager = Events()
    response = event_manager.get_events(limit=limit)
    return jsonify(response)
    
class Events(object):
    """ Class that handles event database calls """
    def __init__(self):
        daiquiri.setup(level=logging.INFO)
        self.logger = daiquiri.getLogger(__name__)

        self.database = Database()

    def get_events(self, limit=25):
        """ Fetches the most recent events from the database """
        df = self.database.read_table('event_aggregates', limit=limit)
        response = [json.loads(df.loc[i].to_json()) for i in df.index]
        return response

