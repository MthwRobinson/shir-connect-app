"""
REST Endpoints for events
A user must be authenticated to use end points
Includes:
    1. Flask routes with /event/<event_id> paths
    2. Flask routes with /events path
    3. Events class to manage database calls
"""
import datetime
from io import StringIO

from flask import Blueprint, jsonify, make_response, request
from flask_jwt_extended import jwt_required, get_jwt_identity

from shir_connect.database.database import Database
from shir_connect.database.events import Events
import shir_connect.configuration as conf
from shir_connect.services.utils import validate_inputs

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

    fake_data = request.args.get('fake_data')
    fake_data = fake_data is not None and fake_data == 'true'
    event = event_manager.get_event(event_id, fake=fake_data)
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
    page = request.args.get('page')
    order = request.args.get('order')
    sort = request.args.get('sort')
    q = request.args.get('q')
    fake_data = request.args.get('fake_data')
    
    limit = 25 if not limit else int(limit)
    page = 1 if not page else int(page)
    order = 'desc' if not order else order
    sort = 'start_datetime' if not sort else sort
    fake_data = fake_data is not None and fake_data == 'true'

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

    response = event_manager.get_events(limit=limit, page=page,
                                        order=order, sort=sort,
                                        q=q, where=where,
                                        fake=fake_data)
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
    
    fake_data = request.args.get('fake_data')
    fake_data = fake_data is not None and fake_data == 'true'
    response = event_manager.get_event_locations(fake=fake_data)
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

    buffer = StringIO()
    df.to_csv(buffer, encoding='utf-8', index=False)
    output = make_response(buffer.getvalue())
    output.headers["Content-Disposition"] = "attachment; filename=export.csv"
    output.headers["Content-type"] = "text/csv"
    return output
