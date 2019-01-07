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

import trs_dashboard.configuration as conf
from trs_dashboard.database.database import Database

user_management = Blueprint('user_management', __name__)

@user_management.route('/service/user', methods=['POST'])
@jwt_required
def user_register():
    """ Registers a new user """
    user_management = UserManagement()
    jwt_user = get_jwt_identity()
    admin_user = user_management.get_user(jwt_user)
    if admin_user['role'] != 'admin':
        response = {'message': 'only admins can add users'}
        return jsonify(response), 403

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

@user_management.route('/service/user/<username>', methods=['DELETE'])
@jwt_required
def delete_user(username):
    """ Deletes a user """
    user_management = UserManagement()
    jwt_user = get_jwt_identity()
    admin_user = user_management.get_user(jwt_user)
    if admin_user['role'] != 'admin':
        response = {'message': 'only admins can delete users'}
        return jsonify(response), 403
    user_management.delete_user(username)
    response = {'message': 'user %s has been removed'%(username)}
    return jsonify(response), 204

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

@user_management.route('/service/user/update-role', methods=['POST'])
@jwt_required
def update_role():
    """ Updates the role for the user in the post body """
    user_management = UserManagement()
    jwt_user = get_jwt_identity()
    admin_user = user_management.get_user(jwt_user)
    if admin_user['role'] != 'admin':
        response = {'message': 'only admins can update roles'}
        return jsonify(response), 403
    else:
        if 'username' not in request.json:
            response = {'message': 'username required in post body'}
            return jsonify(response), 400
        if 'role' not in request.json:
            response = {'message': 'role required in post body'}
            return jsonify(response), 400

        username = request.json['username']
        role = request.json['role']
        updated = user_management.update_role(username, role)
        if updated:
            response = {'message': 'role update for %s'%(username)}
            return jsonify(response), 201

@user_management.route('/service/user/update-access', methods=['POST'])
@jwt_required
def update_access():
    """ Updates the accesses for the user in the post body """
    user_management = UserManagement()
    jwt_user = get_jwt_identity()
    admin_user = user_management.get_user(jwt_user)
    if admin_user['role'] != 'admin':
        response = {'message': 'only admins can update accesses'}
        return jsonify(response), 403
    else:
        if 'username' not in request.json:
            response = {'message': 'username required in post body'}
            return jsonify(response), 400
        if 'modules' not in request.json:
            response = {'message': 'role required in post body'}
            return jsonify(response), 400

        username = request.json['username']
        modules = request.json['modules']
        user_management.update_access(username, modules)
        response = {'message': 'role updated for %s'%(username)}
        return jsonify(response), 201

@user_management.route('/service/user/reset-password', methods=['POST'])
@jwt_required
def reset_password():
    """ Resets the password for the user in the post body """
    user_management = UserManagement()
    jwt_user = get_jwt_identity()
    admin_user = user_management.get_user(jwt_user)
    if admin_user['role'] != 'admin':
        response = {'message': 'only admins can reset password'}
        return jsonify(response), 403
    else:
        if 'username' not in request.json:
            response = {'message': 'username required in post body'}
            return jsonify(response), 400
        if 'password' not in request.json:
            response = {'message': 'password required in post body'}
            return jsonify(response), 400
        if 'password2' not in request.json:
            response = {'message': 'password2 required in post body'}
            return jsonify(response), 400
        
        username = request.json['username']
        password = request.json['password']
        password2 = request.json['password2']
        if password != password2:
            response = {'message': 'passwords must match'}
            return jsonify(response), 400
        else:
            user_management.update_password(username, password)
            response = {'message': 'role updated for %s'%(username)}
            return jsonify(response), 201

@user_management.route('/service/users/list', methods=['GET'])
@jwt_required
def list_users():
    """ Returns a list of the current active users """
    user_management = UserManagement()
    jwt_user = get_jwt_identity()
    admin_user = user_management.get_user(jwt_user)
    if admin_user['role'] != 'admin':
        response = {'message': 'only admins can reset password'}
        return jsonify(response), 403
    else:
        users = user_management.list_users()
        return jsonify(users), 200

class UserManagement(object):
    """ Class that handles user centric REST operations """
    def __init__(self):
        daiquiri.setup(level=logging.INFO)
        self.logger = daiquiri.getLogger(__name__)

        self.database = Database()

        self.access_groups = conf.ACCESS_GROUPS
        self.user_roles = conf.USER_ROLES

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

    def update_role(self, username, role):
        """ 
        Updates the role for the user.
        The two types of users are admin and standard
        """
        if role not in self.user_roles:
            return False
        else:
            value = "'%s'"%(role)
            self.database.update_column(
                table='users',
                item_id=username,
                column='role',
                value=value
            )
            return True

    def update_access(self, username, modules):
        """
        Updates the modules thate are available for the user.
        The available types are events, members, trends and map
        """
        mods = [x for x in modules if x in self.access_groups]
        value = "'{" + ','.join(['"%s"'%(x) for x in mods]) + "}'"
        self.database.update_column(
            table='users',
            item_id=username,
            column='modules',
            value=value
        )

    def list_users(self):
        """ Lists all of the active users """
        df = self.database.read_table('users')
        users = []
        for i in df.index:
            user = dict(df.loc[i])
            del user['password']
            users.append(user)
        return users

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
