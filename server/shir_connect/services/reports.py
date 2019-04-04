"""
REST Endpoints for reports
A user must be authenticated to use these
Includes:
    1. Flask routes with /report paths
"""
import datetime

from flask import Blueprint, jsonify, request 
from flask_jwt_extended import jwt_required, get_jwt_identity
import pandas as pd

from shir_connect.database.events import Events
import shir_connect.configuration as conf
import shir_connect.services.utils as utils

reports = Blueprint('reports', __name__)

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
    
    

