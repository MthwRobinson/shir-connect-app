"""
REST Endpoints for members
A user must be authenticated to use end points
Includes:
    1. Flask routes with /member/<member_id> paths
    2. Flask routes with /members path
    3. Members class to manage database calls
"""
from flask import Blueprint, abort, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity

import shir_connect.configuration as conf
from shir_connect.database.database import Database
from shir_connect.database.members import Members
from shir_connect.services.utils import validate_inputs

members = Blueprint('members', __name__)

@members.route('/service/member/authorize', methods=['GET'])
@jwt_required
def member_authorize():
    """ Checks to see if the user is authorized to see members """
    database = Database()
    jwt_user = get_jwt_identity()
    user = database.get_item('users', jwt_user)
    if conf.MEMBER_GROUP not in user['modules']:
        response = {'message': '%s does not have access to members'%(jwt_user)}
        return jsonify(response), 403
    else:
        del user['password']
        return jsonify(user), 200

@members.route('/service/member', methods=['GET'])
@jwt_required
@validate_inputs(fields={
    'firstName': {'type': 'str', 'max': 30},
    'lastName': {'type': 'str', 'max': 30}
})
def get_member():
    """ Pulls a members information from the database """
    member_manager = Members()
    jwt_user = get_jwt_identity()
    user = member_manager.database.get_item('users', jwt_user)
    if conf.MEMBER_GROUP not in user['modules']:
        response = {'message': '%s does not have access to members'%(jwt_user)}
        return jsonify(response), 403

    first_name = request.args.get('firstName')
    if not first_name:
        response = {'message': 'first name required'}
        return jsonify(response), 404

    last_name = request.args.get('lastName')
    if not last_name:
        response = {'message': 'last name required'}
        return jsonify(response), 404

    member = member_manager.get_member(first_name, last_name)
    if member:
        return jsonify(member)
    else:
        response = {'message': 'not found'}
        return jsonify(response), 404

@members.route('/service/members', methods=['GET'])
@jwt_required
@validate_inputs(fields={'max_age': {'type': 'int'},
                         'min_age': {'type': 'int'}})
def get_members():
    """ Pulls the list of members from the database """
    member_manager = Members()
    jwt_user = get_jwt_identity()
    user = member_manager.database.get_item('users', jwt_user)
    if conf.MEMBER_GROUP not in user['modules']:
        response = {'message': '%s does not have access to members'%(jwt_user)}
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
        order = 'asc'
    sort = request.args.get('sort')
    if not sort:
        sort = 'last_name'
    q = request.args.get('q')

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

    response = member_manager.get_members(limit=limit, page=page, order=order,
                                          sort=sort, q=q, where=where)
    return jsonify(response)

@members.route('/service/members/upload', methods=['POST'])
@jwt_required
def upload_members():
    """ Uploads membership data as a .csv or excel file """
    member_manager = Members()
    jwt_user = get_jwt_identity()
    user = member_manager.database.get_item('users', jwt_user)
    if user['role'] != conf.ADMIN_ROLE:
        response = {'message': 'only admins can upload files'}
        return jsonify(response), 403

    good_upload = member_manager.upload_file(request)
    if good_upload:
        response = {'message': 'success'}
        return jsonify(response)
    else:
        abort(422)
