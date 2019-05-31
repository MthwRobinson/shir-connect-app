"""
REST Endpoints for reports
A user must be authenticated to use these
Includes:
    1. Flask routes with /report paths
"""
from copy import deepcopy
import datetime

from flask import Blueprint, jsonify, request 
from flask_jwt_extended import jwt_required, get_jwt_identity
import pandas as pd

from shir_connect.database.database import Database
from shir_connect.database.events import Events
from shir_connect.database.members import Members
import shir_connect.configuration as conf
import shir_connect.services.utils as utils

reports = Blueprint('reports', __name__)

REPORT_QUARTERS = [("01-01", "04-01"), ("04-01", "07-01"),
                   ("07-01", "10-01"), ("10-01", "01-01")]

def get_quarters(n=3):
    """Computes the current quarter of the year."""
    now = datetime.datetime.now()
    year = now.year
    quarter = pd.Timestamp(now).quarter
    quarters = [(year, quarter)]
    for i in range(n):
        if quarter == 1:
            quarter = 4
            year -= 1
        else:
            quarter -= 1
        quarters.append((year, quarter))
    quarters.reverse()
    return quarters

def get_quarterly_event_counts(quarters, event_manager):
    """Pulls the quarterly event counts for the specified quarters."""
    response = {}
    for pair in quarters:
        year = pair[0]
        quarter = pair[1]
        quarter_desc = '{}-Q{}'.format(year, quarter)
        date_range = REPORT_QUARTERS[quarter-1]
        start = '{}-{}'.format(year, date_range[0])
        if quarter == 4:
            year += 1
        end = '{}-{}'.format(year, date_range[1])
        response[quarter_desc] = event_manager.event_group_counts(start, end)
    return response

def get_quarterly_new_members(quarters, members):
    """Pulls the quarterly event counts for the specified quarters."""
    response = {}
    for pair in quarters:
        year = pair[0]
        quarter = pair[1]
        quarter_desc = '{}-Q{}'.format(year, quarter)
        date_range = REPORT_QUARTERS[quarter-1]
        start = '{}-{}'.format(year, date_range[0])
        if quarter == 4:
            year += 1
        end = '{}-{}'.format(year, date_range[1])
        response[quarter_desc] = members.count_new_households(start, end)
    return response

def convert_counts_to_string(response):
    """Converts ints to string so they are JSON serializable."""
    response = deepcopy(response)
    for key in response:
        for entry in response[key]:
            response[key][entry] = str(response[key][entry])
    return response

def build_locations_pct(response, common_locations=None):
    """Builds the locations data as percentages to use in the
    'Where do members live?' table and bar chart."""
    if not common_locations:
        common_locations = _find_common_locations(response)
    percentages = {}
    for key in response:
        percentages[key] = {}
        locations = response[key]
        total = _get_list_key(locations, 'location', 'All')
        for location in locations:
            location_name = location['location']
            if location_name in common_locations:
                pct = location['total'] / total['total']
                percentages[key][location_name] = pct
        total_pct = sum([percentages[key][k] for k in percentages[key]])
        percentages[key]['Other'] = 1 - total_pct
    return percentages

def _find_common_locations(response):
    """Finds locations that are in every category."""
    sets = []
    for key in response:
        key_locations = set()
        locations = response[key]
        for location in locations:
            location_name = location['location']
            if location_name not in ['All', 'Other']:
                key_locations.add(location_name)
        sets.append(key_locations)

    for i, set_ in enumerate(sets):
        if i == 0:
            common_locations = set_
        else:
            common_locations = common_locations.intersection(set_)
    return common_locations

def _get_list_key(list_, key, value):
    """Pulls the corresponding item from a list of dicts."""
    for item in list_:
        if key in item:
            if item[key] == value:
                return item
    return None

@reports.route('/service/report/events/count', methods=['GET'])
@jwt_required
def get_report_event_count():
    """Pulls the event counts for the current report."""
    event_manager = Events()
    jwt_user = get_jwt_identity()
    has_access = utils.check_access(jwt_user, conf.REPORT_GROUP,
                                    event_manager.database)
    if not has_access:
        response = {'message': '{} does not have access to reports.'.format(jwt_user)}
        return jsonify(response), 403

    quarters = get_quarters(3)
    response = get_quarterly_event_counts(quarters, event_manager)
    response = convert_counts_to_string(response)
    return jsonify(response)

@reports.route('/service/report/members/new/count', methods=['GET'])
@jwt_required
def get_new_member_count():
    """Pulls the new event counts by quarter."""
    members = Members()
    jwt_user = get_jwt_identity()
    has_access = utils.check_access(jwt_user, conf.REPORT_GROUP,
                                    members.database)
    if not has_access:
        response = {'message': '{} does not have access to reports.'.format(jwt_user)}
        return jsonify(response), 403

    quarters = get_quarters(19)
    response = get_quarterly_new_members(quarters, members)
    response = {k: str(response[k]) for k in response}
    return jsonify(response)

@reports.route('/service/report/members/demographics', methods=['GET'])
@jwt_required
def get_member_demographics():
    """Pulls the current membership demographics."""
    members = Members()
    jwt_user = get_jwt_identity()
    has_access = utils.check_access(jwt_user, conf.REPORT_GROUP,
                                    members.database)

    if not has_access:
        response = {'message': '{} does not have access to reports.'.format(jwt_user)}
        return jsonify(response), 403
    
    only = request.args.get('only')
    new_members = only == 'new_members'

    response = members.get_demographics(new_members=new_members)
    return jsonify(response)

@reports.route('/service/report/members/locations', methods=['GET'])
@jwt_required
def get_member_locations():
    """Pulls in the current breakdown of member location."""
    members = Members()
    jwt_user = get_jwt_identity()
    has_access = utils.check_access(jwt_user, conf.REPORT_GROUP,
                                    members.database)
    
    if not has_access:
        response = {'message': '{} does not have access to reports.'.format(jwt_user)}
        return jsonify(response), 403
    
    level = request.args.get('level')
    level = level if level else 'city'

    now = datetime.datetime.now()
    year_ago = str(now - datetime.timedelta(days=365))[:10]
    five_years_ago = str(now - datetime.timedelta(days=365*5))[:10]

    # Hard coding these settings for now, but we can move these
    # to the config files if a client wants something different
    response = {}
    response['all_members'] = members.get_member_locations('city', limit=8)
    response['new_members'] = members.get_member_locations('city', limit=8,
                                                           start=year_ago)
    response['year_ago'] = members.get_member_locations('city', limit=8,
                                                           end=year_ago)
    response['five_years_ago'] = members.get_member_locations('city', limit=8,
                                                           end=five_years_ago)
    common_locations = _find_common_locations(response)
    response['percentages'] = build_locations_pct(response, common_locations)
    response['common_locations'] = list(common_locations)
    return jsonify(response)

@reports.route('/service/report/members/new', methods=['GET'])
@jwt_required
def get_new_members():
    """Pulls in a list of the most recent members of the Congregation."""
    database = Database()
    jwt_user = get_jwt_identity()
    has_access = utils.check_access(jwt_user, conf.REPORT_GROUP, database)

    if not has_access:
        response = {'message': '{} does not have access to reports.'.format(jwt_user)}
        return jsonify(response), 403

    limit_param = request.args.get('limit')
    limit = limit_param if limit_param else 25
    new_members = database.read_table('members_view', limit=limit,
                                      order='desc', sort='membership_date')
    response = database.to_json(new_members)
    return jsonify(response)

@reports.route('/service/report/members/households/count', methods=['GET'])
@jwt_required
def get_households_by_year():
    """Pulls in a list of the most recent members of the Congregation."""
    members = Members()
    jwt_user = get_jwt_identity()
    has_access = utils.check_access(jwt_user, conf.REPORT_GROUP, members.database)

    if not has_access:
        response = {'message': '{} does not have access to reports.'.format(jwt_user)}
        return jsonify(response), 403

    years = request.args.get('years')
    years = int(years) if years else 10

    tally = request.args.get('tally')
    tally = 'households' if not tally else tally

    now = datetime.datetime.now()
    end = now.year
    start = end - years

    if tally == 'resignations':
        response = members.get_resignations_by_year(start, end)
    else:
        response = members.get_households_by_year(start, end)
    return jsonify(response)

@reports.route('/service/report/members/households/type', methods=['GET'])
@jwt_required
def get_household_types():
    """Pulls in a list of the most recent members of the Congregation."""
    members = Members()
    jwt_user = get_jwt_identity()
    has_access = utils.check_access(jwt_user, conf.REPORT_GROUP, members.database)

    if not has_access:
        response = {'message': '{} does not have access to reports.'.format(jwt_user)}
        return jsonify(response), 403

    response = {}
    all_households = members.get_household_types()
    for item in all_households:
        item['total'] = str(item['total'])
    response['all_households'] = all_households
    
    now = datetime.datetime.now()
    year_ago = now - datetime.timedelta(days=365)
    new_start = str(year_ago)[:10]

    new_households = members.get_household_types(start=new_start)
    for item in new_households:
        item['total'] = str(item['total'])
    response['new_households'] = new_households

    return jsonify(response)

@reports.route('/service/report/members/resignations/type', methods=['GET'])
@jwt_required
def get_resignation_types():
    """Breaks down resignations over hte past year by type."""
    members = Members()
    jwt_user = get_jwt_identity()
    has_access = utils.check_access(jwt_user, conf.REPORT_GROUP, members.database)

    if not has_access:
        response = {'message': '{} does not have access to reports.'.format(jwt_user)}
        return jsonify(response), 403

    resignation_types = members.get_resignation_types()
    return jsonify(resignation_types)
