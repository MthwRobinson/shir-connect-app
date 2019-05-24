"""
REST enpoints for participants
Requires authentication
Includes:
    1. Flask routes with /participant paths
    2. Flask routes with /participants paths
"""
from flask import Blueprint, abort, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity

import shir_connect.configuration as conf
from shir_connect.database.database import Database
from shir_connect.database.participants import Participants
from shir_connect.services.utils import validate_inputs

participants = Blueprint('participants', __name__)

@participants.route('/service/participant/<participant_id>', methods=['GET'])
@jwt_required
@validate_inputs(fields={'event_id': {'type': 'int'}})
def get_participant(participant_id):
    """ Pulls a participants information from the database """
    participant_manager = Participants()
    jwt_user = get_jwt_identity()
    user = participant_manager.database.get_item('users', jwt_user)
    if conf.MEMBER_GROUP not in user['modules']:
        response = {'message': '%s does not have access to participants'%(jwt_user)}
        return jsonify(response), 403

    fake_data = request.args.get('fake_data')
    fake_data = fake_data is not None and fake_data == 'true'
    participant = participant_manager.get_participant(participant_id, fake=fake_data)
    if participant:
        return jsonify(participant)
    else:
        response = {'message': 'not found'}
        return jsonify(response), 404

@participants.route('/service/participants', methods=['GET'])
@jwt_required
@validate_inputs(fields={'max_age': {'type': 'int'},
                         'min_age': {'type': 'int'}})
def get_participants():
    """ Pulls the list of participants from the database """
    participant_manager = Participants()
    jwt_user = get_jwt_identity()
    user = participant_manager.database.get_item('users', jwt_user)
    if conf.MEMBER_GROUP not in user['modules']:
        msg = "{} does not have access to participants."
        response = {'message': msg.format(jwt_user)}
        return jsonify(response), 403

    limit = request.args.get('limit')
    page = request.args.get('page')
    order = request.args.get('order')
    sort = request.args.get('sort')
    q = request.args.get('q')
    fake_data = request.args.get('fake_data')
    
    limit = 25 if not limit else int(limit)
    page = 1 if not page else int(page)
    order = 'asc' if not order else order
    sort = 'last_name' if not sort else sort
    fake_data = fake_data is not None and fake_data == 'true'

    where = []
    max_age = request.args.get('max_age')
    min_age = request.args.get('min_age')
    if max_age or min_age:
        conditions = {}
        if max_age:
            conditions['<='] = max_age
        if min_age:
            conditions['>='] = min_age
        where.append(('age', conditions))

    response = participant_manager.get_participants(limit=limit, page=page,
                                                    order=order, sort=sort,
                                                    q=q, where=where,
                                                    fake=fake_data)
    return jsonify(response)
