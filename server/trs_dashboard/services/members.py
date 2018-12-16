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
import numpy as np
from werkzeug.utils import secure_filename

import trs_dashboard.configuration as conf
from trs_dashboard.database.database import Database

members = Blueprint('members', __name__)

@members.route('/service/member', methods=['GET'])
@jwt_required
def get_member():
    """ Pulls a members information from the database """
    first_name = request.args.get('firstName')
    if not first_name:
        response = {'message': 'first name required'}
        return jsonify(response), 404

    last_name = request.args.get('lastName')
    if not last_name:
        response = {'message': 'last name required'}
        return jsonify(response), 404

    member_manager = Members()
    member = member_manager.get_member(first_name, last_name)
    if member:
        return jsonify(member)
    else:
        response = {'message': 'not found'}
        return jsonify(response), 404


@members.route('/service/members', methods=['GET'])
@jwt_required
def get_members():
    """ Pulls the list of members from the database """
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

    member_manager = Members()
    response = member_manager.get_members(
        limit=limit,
        page=page,
        order=order,
        sort=sort,
        q=q
    )
    return jsonify(response)

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
        self.column_mapping = conf.COLUMN_MAPPING
        self.member_columns = conf.MEMBER_COLUMNS
        self.spouse_columns = conf.SPOUSE_COLUMNS
        self.home_path = conf.HOMEPATH

    def get_member(self, first_name, last_name):
        """ Pulls the information for a member """
        sql = """
            SELECT DISTINCT
                CASE
                    WHEN a.first_name IS NOT NULL then INITCAP(a.first_name)
                    ELSE INITCAP(c.first_name)
                END as first_name,
                CASE
                    WHEN a.last_name IS NOT NULL then INITCAP(a.last_name)
                    ELSE INITCAP(c.last_name)
                END as last_name,
                date_part('year', now()) 
                        - date_part('year', birth_date
                ) as age,
                CASE
                    WHEN c.email IS NOT NULL THEN c.email
                    ELSE a.email
                END as email,
                CASE
                    WHEN c.first_name IS NOT NULL THEN TRUE
                    ELSE FALSE
                END as is_member,
                membership_date
            FROM {schema}.members_view c
            FULL JOIN {schema}.attendees a
            ON (lower(a.first_name) = lower(c.first_name)
            AND lower(a.last_name) = lower(c.last_name))
            LEFT JOIN {schema}.events b
            ON a.event_id = b.id
            WHERE (
                (
                    lower(a.first_name) = lower('{first_name}')
                    AND lower(a.last_name) = lower('{last_name}')
                ) OR
                (
                    lower(c.first_name) = lower('{first_name}')
                    AND lower(c.last_name) = lower('{last_name}')

                )
            )
        """.format(
            schema=self.database.schema, 
            first_name=first_name, 
            last_name=last_name
        )

        df = pd.read_sql(sql, self.database.connection)
        df = df.where((pd.notnull(df)), None)
        if len(df) > 0:
            col_to_string = ['membership_date']
            member = dict(df.loc[0])
            for column in member.keys():
                if type(member[column]) == int:
                    col_to_string.append(column)
                elif isinstance(member[column], np.int64):
                    col_to_string.append(column)
                elif member[column] in [True, False]:
                    col_to_string.append(column)
                if column in col_to_string:
                    member[column] = str(member[column])
            member['events'] = self.get_member_events(first_name, last_name)
            return member
        else:
            return None

    def get_member_events(self, first_name, last_name):
        """ Pulls information for events a member has attended """
        sql = """
            SELECT DISTINCT
                b.id as event_id,
                b.start_datetime,
                b.name,
                d.latitude,
                d.longitude
            FROM {schema}.attendees a
            LEFT JOIN {schema}.events b
            ON a.event_id = b.id
            LEFT JOIN {schema}.venues d
            ON b.venue_id = d.id
            WHERE (
                lower(a.first_name) = lower('{first_name}')
                AND lower(a.last_name) = lower('{last_name}')
            )
            ORDER BY start_datetime DESC
        """.format(
            schema=self.database.schema,
            first_name=first_name,
            last_name=last_name
        )
        df = pd.read_sql(sql, self.database.connection)
        df = df.where((pd.notnull(df)), None)
        if len(df) > 0:
            events = []
            for i in df.index:
                event = dict(df.loc[i])
                event['start_datetime'] = str(event['start_datetime'])
                events.append(event)
            return events
        else:
            return []

    def get_members(self, limit=None, page=None, order=None, sort=None, q=None):
        """ Pulls a list of members from the database """
        if q:
            query = ('last_name', q)
        else:
            query = None

        df = self.database.read_table(
            'participants',
            limit=limit,
            page=page,
            order=order,
            sort=sort,
            query=query
        )
        count = self.database.count_rows('members_view', query=query)

        pages = int((count/limit)) + 1
        members = self.database.to_json(df)
        response = {'results': members, 'count': str(count), 'pages': pages}
        return response
    
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
        
        # Find the columns that reference the member and the spouse
        df_members = df[self.member_columns].copy()
        df_spouse = df[self.spouse_columns].copy()
        del df

        # Update the columns to match the postgres table
        df_members = self.update_columns(df_members)
        df_spouse = self.update_columns(df_spouse)

        # Combine and clean up the full table
        df = df_members.append(df_spouse)
        df = df.dropna(how='all').copy()
        df = df.reset_index().copy()

        self.database.backup_table('members')
        self.database.truncate_table('members')

        items = []
        for i in df.index:
            item = dict(df.loc[i])
            postal = str(item['postal_code'])
            if '-' in postal:
                postal = postal.split('-')[0]
            if len(postal) != 5:
                postal = None
            item['postal_code'] = postal
            items.append(item)
        self.database.load_items(items, 'members')

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
            if column in self.column_mapping['columns']:
                db_column = self.column_mapping['columns'][column]
                db_columns.append(db_column)
            else:
                db_columns.append(column)
        df.columns = db_columns
        
        # Add columns that aren't present
        pg_columns = self.database.get_columns('members')
        for column in pg_columns:
            if column not in df.columns:
                df.insert(0, column, None)
        df = df[pg_columns].copy()
        
        # Make sure the time columns have the correct type
        for column in df.columns:
            if column in self.column_mapping['time_columns']:
                if 'datetime' not in df.dtypes[column].name:
                    df.loc[:, column] = pd.to_datetime(
                        df[column], 
                        errors='coerce'
                    )
            else:
                if 'object' not in df.dtypes[column].name:
                    df.loc[:, column] = df[column].astype(str)
        
        # Change NaN values to None
        df = df.astype(object)
        df = df.where((pd.notnull(df)), None)

        return df

    def clean_field(self, field):
        """ Removes numbers from the fields """
        field = ''.join([i for i in field if not i.isdigit()])
        field = field.lower().replace(' ','_')
        return field

    def create_dummy_members(self, limit=None, load=False):
        """ Creates dummy membership data for development """
        sql = """
            SELECT DISTINCT first_name, last_name
            FROM {schema}.attendees
        """.format(schema=self.database.schema)
        if limit:
            sql += " LIMIT %s "%(limit)
        df = pd.read_sql(sql, self.database.connection)

        sql = """
            SELECT DISTINCT postal_code
            FROM {schema}.venues
        """.format(schema=self.database.schema)
        postal_table = pd.read_sql(sql, self.database.connection)
        postal_codes = [x for x in postal_table['postal_code']]

        columns = self.database.get_columns('members')
        data = {x: [] for x in columns}
        for i in df.index:
            row = dict(df.loc[i])

            # Generate random birthdays and member ship dates
            interval = 29200
            start = datetime.datetime(1938, 1, 1)
            bday_draw = int(np.random.random()*interval)
            member_draw = int(np.random.random()*(interval-bday_draw))
            bday = start + datetime.timedelta(days=bday_draw)
            member_date = start + datetime.timedelta(days=member_draw)

            # Generate a random zip code
            np.random.shuffle(postal_codes)
            postal_code = postal_codes[0]

            # Generate first name and last name
            if not row['first_name'] or not row['last_name']:
                continue
            else:
                first_name = row['first_name'].title()
                last_name = row['last_name'].title()
                email = row['last_name'] + '@fake.com'

            # Append the dummy data
            data['id'].append('M'+str(i))
            data['first_name'].append(first_name)
            data['last_name'].append(last_name)
            data['nickname'].append(first_name)
            data['birth_date'].append(bday)
            data['membership_date'].append(member_date)
            data['member_religion'].append('Jewish')
            data['postal_code'].append(postal_code)
            data['member_family'].append('Y')
            data['member_type'].append('Member')
            data['email'].append(email)

        df = pd.DataFrame(data)
        if load:
            self.database.truncate_table('members')
            for i in df.index:
                item = dict(df.loc[i])
                self.database.load_item(item, 'members')
            good_columns = self.check_columns()
            if good_columns:
                self.database.refresh_view('members_view')
        else:
            return df


