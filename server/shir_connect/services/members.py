"""
REST Endpoints for members
A user must be authenticated to use end points
Includes:
    1. Flask routes with /member/<member_id> paths
    2. Flask routes with /members path
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

    file_type = request.args.get('file_type')
    file_type = 'members' if not file_type else file_type

    good_upload = member_manager.upload_file(request, file_type=file_type)
    if good_upload:
        response = {'message': 'success'}
        return jsonify(response)
    else:
        abort(422)
