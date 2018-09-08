""" 
REST endpoints for operations pertaining to users
Includes:
    1. Flask routes with /user path
    2. UserManagment class for database calls
"""
import hashlib
import logging

import daiquiri
from flask import Blueprint, abort, jsonify, request
from flask_jwt_simple import create_jwt
import pandas as pd

from trs_dashboard.database.database import Database

user_management = Blueprint('user_management', __name__)

@user_management.route('/service/user/register', methods=['POST'])
def user_register():
    """ Registers a new user """
    if not request.json:
        response = {'message': 'no post body'}
        return jsonify(response), 400

    new_user = request.json
    if 'username' not in new_user  or 'password' not in new_user:
        response = {'message': 'missing key in post body'}
        return jsonify(response), 400

    new_user['id'] = new_user['username']
    user_management = UserManagement()
    status = user_management.add_user(new_user['id'], new_user['password'])
    # Status returns false if user already exists
    if status:
        response = {'message': 'user %s created'%(new_user['id'])}
        return jsonify(response), 201
    else:
        response = {'message': 'user already exists'}
        return jsonify(response), 409

@user_management.route('/service/user/authenticate', methods=['POST'])
def user_authenticate():
    """ Authenticates a user and returns a json web token """
    if not request.json:
        response = {'message': 'no post body'}
        return jsonify(response), 400

    auth_user = request.json
    if 'username' not in auth_user  or 'password' not in auth_user:
        response = {'message': 'missing key in post body'}
        return jsonify(response), 400

    user_management = UserManagement()
    authorized = user_management.authenticate_user(
        username=auth_user['username'],
        password=auth_user['password']
    )
    if authorized:
        msg = 'user %s authenticated'%(auth_user['username'])
        response = {
            'message': msg,
            'jwt': create_jwt(identity=auth_user['username'])
        }
        return jsonify(response), 200
    else:
        msg = 'authentication failed for user %s'%(auth_user['username'])
        response = {'message': msg}
        return jsonify(response), 401

class UserManagement(object):
    """ Class that handles user centric REST operations """
    def __init__(self):
        daiquiri.setup(level=logging.INFO)
        self.logger = daiquiri.getLogger(__name__)

        self.database = Database()

    def get_user(self, username):
        """ Fetches a user from the database """
        return self.database.get_item('users', username)

    def authenticate_user(self, username, password):
        """
        Checks the password of the user
        Returns True if the user is authorized
        """
        user = self.get_user(username)
        if not user:
            return False

        pw = password.encode('utf-8')
        pw_hash = hashlib.sha512(pw).hexdigest()
        if user['password'] == pw_hash:
            return True
        else:
            return False

    def add_user(self, username, password):
        """ Adds a new user to the database """
        # Check to see if the user already exists
        user = self.get_user(username)
        if user:
            return False
        else:
            pw = password.encode('utf-8')
            pw_hash = hashlib.sha512(pw).hexdigest()
            item = {
                'id': username,
                'password': pw_hash
            }
            self.database.load_item(item, 'users')
            return True

    def delete_user(self, username):
        """ Deletes a user from the database """
        self.database.delete_item('users', username)

