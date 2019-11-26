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
from shir_connect.services.utils import validate_inputs, log_request

trends = Blueprint('trends', __name__)

@trends.route('/service/trends/authorize', methods=['GET'])
@jwt_required
def member_authorize():
    """ Checks to see if the user is authorized to see members """
    database = Database()
    jwt_user = get_jwt_identity()
    user = database.get_item('users', jwt_user)

    authorized = conf.TRENDS_GROUP in user['modules']
    log_request(request, jwt_user, authorized)

    if not authorized:
        response = {'message': '%s does not have access to trends'%(jwt_user)}
        return jsonify(response), 403
    else:
        del user['password']
        del user['temporary_password']
        return jsonify(user), 200

@trends.route('/service/trends/monthly-revenue', methods=['GET'])
@jwt_required
def month_revenue():
    """ Finds event revenue aggregated by month """
    trends = Trends()
    jwt_user = get_jwt_identity()
    user = trends.database.get_item('users', jwt_user)

    authorized = conf.TRENDS_GROUP in user['modules']
    log_request(request, jwt_user, authorized)

    if not authorized:
        response = {'message': '%s does not have access to members'%(jwt_user)}
        return jsonify(response), 403

    response = trends.get_monthly_revenue()
    return jsonify(response)

@trends.route('/service/trends/avg-attendance', methods=['GET'])
@jwt_required
def average_attendance():
    """ Finds the avg event attendace by day of week """
    trends = Trends()
    jwt_user = get_jwt_identity()
    user = trends.database.get_item('users', jwt_user)

    authorized = conf.TRENDS_GROUP in user['modules']
    log_request(request, jwt_user, authorized)

    if not authorized:
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
    jwt_user = get_jwt_identity()
    user = trends.database.get_item('users', jwt_user)

    authorized = conf.TRENDS_GROUP in user['modules']
    log_request(request, jwt_user, authorized)

    if not authorized:
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
    jwt_user = get_jwt_identity()
    user = trends.database.get_item('users', jwt_user)

    authorized = conf.TRENDS_GROUP in user['modules']
    log_request(request, jwt_user, authorized)

    if not authorized:
        response = {'message': '%s does not have access to members'%(jwt_user)}
        return jsonify(response), 403

    limit = request.args.get('limit')
    top = request.args.get('top')
    fake_data = request.args.get('fake_data')

    limit = 25 if not limit else int(limit)
    top = 'participant' if not top else top
    fake_data = fake_data is not None and fake_data == 'true'

    response = trends.get_participation(age_group, top, limit, fake=fake_data)
    return jsonify(response)
