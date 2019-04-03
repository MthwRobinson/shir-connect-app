"""
REST Endpoints for trends
A user must be authenticated to use end points
Includes:
    1. Flask routes with /trends path
    2. Trends class to manage database calls
"""
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity

from shir_connect.database.database import Database
from shir_connect.database.trends import Trends
import shir_connect.configuration as conf
from shir_connect.services.utils import validate_inputs

trends = Blueprint('trends', __name__)

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
