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

from shir_connect.database.events import Events
import shir_connect.configuration as conf
import shir_connect.services.utils as utils

reports = Blueprint('reports', __name__)

REPORT_QUARTERS = [("01-01", "04-01"), ("04-01", "07-01"),
                   ("07-01", "10-01"), ("10-01", "01-01")]

def get_quarters():
    """Computes the current quarter of the year."""
    now = datetime.datetime.now()
    year = now.year
    quarter = pd.Timestamp(now).quarter
    quarters = [(year, quarter)]
    for i in range(3):
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

def convert_counts_to_string(response):
    """Converts ints to string so they are JSON serializable."""
    response = deepcopy(response)
    for key in response:
        for entry in response[key]:
            response[key][entry] = str(response[key][entry])
    return response

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

    quarters = get_quarters()
    response = get_quarterly_event_counts(quarters, event_manager)
    response = convert_counts_to_string(response)
    return jsonify(response)
