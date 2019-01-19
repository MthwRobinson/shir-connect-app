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
from flask_jwt_extended import jwt_required, get_jwt_identity
import pandas as pd
import numpy as np
from werkzeug.utils import secure_filename

import trs_dashboard.configuration as conf
from trs_dashboard.database.database import Database
from trs_dashboard.database.member_loader import MemberLoader

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

class Members(object):
    """ Class that handle database operations for members """
    def __init__(self):
        daiquiri.setup(level=logging.INFO)
        self.logger = daiquiri.getLogger(__name__)

        self.database = Database()
        self.member_loader = MemberLoader()

        self.allowed_extensions = conf.ALLOWED_EXTENSIONS

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
        count = self.database.count_rows('participants', query=query)

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
            df = pd.read_csv(file_, encoding='latin-1')
        else:
            df = pd.read_excel(file_)
        return self.member_loader.load(df)

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
