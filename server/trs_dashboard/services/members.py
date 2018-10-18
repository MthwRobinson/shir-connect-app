"""
REST Endpoints for members
A user must be authenticated to use end points
Includes:
    1. Flask routes with /member/<member_id> paths
    2. Flask routes with /members path
    3. Members class to manage database calls
"""
import datetime
import logging

import daiquiri
from flask import Blueprint, abort, jsonify, make_response, request
from flask_jwt_simple import jwt_required
import pandas as pd
from werkzeug.utils import secure_filename

import trs_dashboard.configuration as conf
from trs_dashboard.database.database import Database

members = Blueprint('members', __name__)

@members.route('/service/members/upload', methods=['POST'])
@jwt_required
def upload_members():
    """ Uploads membership data as a .csv or excel file """
    member_manager = Members()
    good_upload = member_manager.upload_file(request)
    if good_upload:
        response = {'message': 'success'}
        return jsonify(response)
    else:
        abort(422)

class Members(object):
    """ Class that handle database operations for members """
    def __init__(self):
        daiquiri.setup(level=logging.INFO)
        self.logger = daiquiri.getLogger(__name__)

        self.database = Database()
        self.allowed_extensions = conf.ALLOWED_EXTENSIONS
        self.member_columns = conf.MEMBER_COLUMNS
    
    def upload_file(self, request):
        """ Reads the file and uploads it to the database """
        # Check the filetype
        file_ = request.files['file']
        filename = file_.filename
        if not self.valid_extension(filename):
            return False

        # Convert the file to a dataframe
        if filename.endswith('.csv'):
            df = pd.read_csv(file_)
        else:
            df = pd.read_excel(file_)

        df = self.update_columns(df)
        self.database.backup_table('members')
        self.database.truncate_table('members')
        for i in df.index:
            item = dict(df.loc[i])
            self.database.load_item(item, 'members')

        good_columns = self.check_columns()
        if good_columns:
            self.database.refresh_view('members_view')
        else:
            self.logger.warning('Column mismatch in upload')
            self.database.revert_table('members')
            return False

        return True

    def valid_extension(self, filename):
        """ Checks to make sure the filename has a valid extension """
        for extension in self.allowed_extensions:
            if filename.endswith(extension):
                return True
        return False

    def check_columns(self):
        """ Checks to make sure the columns are the same in the new table """
        new_columns = self.database.get_columns('members')
        old_columns = self.database.get_columns('members_backup')
        for column in new_columns:
            if column not in old_columns:
                return False
        return True

    def update_columns(self, df):
        """ Checks to see if the dataframe columns are valid """
        # Update the column names to match the postgres table
        columns = [self.clean_field(x) for x in df.columns]
        db_columns = []
        for column in columns:
            if column in self.member_columns['columns']:
                db_column = self.member_columns['columns'][column]
                db_columns.append(db_column)
            else:
                db_columns.append(column)
        df.columns = db_columns
        
        # Add columns that aren't present
        pg_columns = self.database.get_columns('members')
        for column in pg_columns:
            if column not in df.columns:
                df[column] = None
        
        # Change NaN values to None
        df = df.where((pd.notnull(df)), None)
        
        # Make sure the time columns have the correct type
        for column in df.columns:
            if column in self.member_columns['time_columns']:
                if 'datetime' not in df.dtypes[column].name:
                    df[column] = pd.to_datetime(df[column])
            else:
                if 'object' not in df.dtypes[column].name:
                    df[column] = df[column].astype(str)

        return df

    def clean_field(self, field):
        """ Removes numbers from the fields """
        field = ''.join([i for i in field if not i.isdigit()])
        field = field.lower().replace(' ','_')
        return field
                

