"""
REST endpoints for exporting files
A user must be authenticated to export files
Includes:
    1. Flask routes with /export path
    2. Export class to manage exports
"""
import csv
import datetime
from io import StringIO
import logging

import daiquiri
from flask import Blueprint, make_response
from flask_jwt_simple import jwt_required
import pandas as pd

from trs_dashboard.database.database import Database

file_export = Blueprint('file_export', __name__)

daiquiri.setup(level=logging.INFO)
LOGGER = daiquiri.getLogger(__name__)

@file_export.route('/service/export/event_aggregates', methods=['GET'])
@jwt_required
def export_event_aggregates():
    """ Exports the event aggregates as a csv """
    database = Database()
    df = database.read_table('event_aggregates')
    # Delete ticket type because CSV has issues with JSON columns
    del df['ticket_type']

    today = str(datetime.datetime.now())[:10]
    filename = 'event_aggregates_%s.csv'%(today)

    buffer = StringIO()
    df.to_csv(buffer, encoding='utf-8', index=False)
    output = make_response(buffer.getvalue())
    output.headers["Content-Disposition"] = "attachment; filename=export.csv"
    output.headers["Content-type"] = "text/csv"
    return output
