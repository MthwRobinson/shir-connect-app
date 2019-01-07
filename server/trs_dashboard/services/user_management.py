""" 
REST endpoints for operations pertaining to users
A user must be authenticated to register a new user
Includes:
    1. Flask routes with /user path
    2. UserManagment class for database calls
"""
import hashlib
import logging

import daiquiri
from flask import Blueprint, abort, jsonify, request
from flask_jwt_simple import create_jwt, jwt_required, get_jwt_identity
import pandas as pd

from trs_dashboard.database.database import Database

user_management = Blueprint('user_management', __name__)

@user_management.route('/service/user/register', methods=['POST'])
@jwt_required
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

@user_management.route('/service/user/authorize', methods=['GET'])
@jwt_required
def user_authorize():
    """ Returns user authorization and role metadata """
    username = get_jwt_identity()
    user_management = UserManagement()
    user = user_management.get_user(username)
    if not user:
        response = {'message': 'user not found'}
        return jsonify(response), 400
    else:
        del user['password']
        return jsonify(user), 200

@user_management.route('/service/user/change-password', methods=['POST'])
@jwt_required
def change_password():
    """ Updates the password for the user """
    if not request.json:
        response = {'message': 'no post body'}
        return jsonify(response), 400
    else:
        # Check the post body for the correct keys
        if 'old_password' not in request.json:
            response = {'message': 'old_password missing in post body'}
            return jsonify(response), 400
        if 'new_password' not in request.json:
            response = {'message': 'new_password missing in post body'}
            return jsonify(response), 400
        if 'new_password2' not in request.json:
            response = {'message': 'new_password2 missing in post body'}
            return jsonify(response), 400

        # Check to see if the old password was correct
        user_management = UserManagement()
        old_password = request.json['old_password']
        username = get_jwt_identity()
        authorized = user_management.authenticate_user(
            username=username,
            password=old_password
        )
        if not authorized:
            response = {'message': 'old password was incorrect'}
            return jsonify(response), 400

        # Check to make sure the two new passwords match
        new_password = request.json['new_password']
        new_password2 = request.json['new_password2']
        if new_password != new_password2:
            response = {'message': 'new passwords did not match'}
            return jsonify(response), 400

        # Update the user's password
        updated = user_management.update_password(username, new_password)
        if updated:
            response = {'message': 'password updated for %s'%(username)}
            return jsonify(response), 201
        else:
            response = {'message': 'password update failed'}
            return jsonify(response), 400

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
        
        pw_hash = self.hash_pw(password)
        if user['password'] == pw_hash:
            return True
        else:
            return False

    def add_user(self, username, password, 
                 role='standard', modules=[]):
        """ Adds a new user to the database """
        complex_enough = self.check_pw_complexity(password)
        if not complex_enough:
            return False

        # Check to see if the user already exists
        user = self.get_user(username)
        if user:
            return False
        else:
            pw_hash = self.hash_pw(password)
            item = {
                'id': username,
                'password': pw_hash
            }
            self.database.load_item(item, 'users')
            return True

    def delete_user(self, username):
        """ Deletes a user from the database """
        self.database.delete_item('users', username)

    def hash_pw(self, password):
        """ Hashes a password """
        pw = password.encode('utf-8')
        pw_hash = hashlib.sha512(pw).hexdigest()
        return pw_hash

    def update_password(self, username, password):
        """ Updates the password for a user. """
        complex_enough = self.check_pw_complexity(password)
        if not complex_enough:
            return False

        # Check to see if the user exists
        user = self.get_user(username)
        if user:
            pw_hash = self.hash_pw(password)
            pw_value = "'%s'"%(pw_hash)
            self.database.update_column(
                table='users',
                item_id=username,
                column='password',
                value=pw_value
            )
            return True
        else:
            return False

    def check_pw_complexity(self, password):
        """ Checks to ensure a password is sufficiently complex """
        if len(password) < 10:
            return False
        elif password.isalnum():
            return False
        elif password.islower():
            return False
        elif password.isupper():
            return False
        else:
            return True
