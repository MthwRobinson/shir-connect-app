"""
REST endpoints for operations pertaining to users
A user must be authenticated to register a new user
Includes:
    1. Flask routes with /user path
    2. UserManagment class for database calls
"""
from flask import Blueprint, jsonify, request
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    get_jwt_identity,
    jwt_refresh_token_required,
    jwt_required,
    set_access_cookies,
    set_refresh_cookies,
    unset_jwt_cookies
)

import shir_connect.configuration as conf
from shir_connect.database.user_management import UserManagement

user_management = Blueprint('user_management', __name__)

@user_management.route('/service/user', methods=['POST'])
@jwt_required
def user_register():
    """ Registers a new user """
    user_management = UserManagement()
    # Only and admin can create a new user
    jwt_user = get_jwt_identity()
    admin_user = user_management.get_user(jwt_user)
    if admin_user['role'] != 'admin':
        response = {'message': 'only admins can add users'}
        return jsonify(response), 403

    # Check to make sure there is a request body
    if not request.json:
        response = {'message': 'no post body'}
        return jsonify(response), 400

    # The username must be in there request
    new_user = request.json
    if 'username' not in new_user:
        response = {'message': 'missing key in post body'}
        return jsonify(response), 400

    # Use default roles and modules if they are not present
    if 'role' not in new_user:
        new_user['role'] = 'standard'
    if 'modules' not in new_user:
        new_user['modules'] = []

    # Generate a password for the user
    new_user['password'] = user_management.generate_password()

    status = user_management.add_user(
        username=new_user['username'],
        password=new_user['password'],
        role=new_user['role'],
        modules=new_user['modules']
    )
    # Status returns false if user already exists
    if status:
        response = {
            'message': 'user %s created'%(new_user['username']),
            'password': new_user['password']
        }
        return jsonify(response), 201
    else:
        response = {'message': 'bad request'}
        return jsonify(response), 400

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
    """
    Authenticates a user and returns a json web token
    In the response body, refresh_token is the refresh token
        and jwt is the access token
    """
    if not request.json:
        response = {'message': 'no post body'}
        return jsonify(response), 400

    auth_user = request.json
    if 'username' not in auth_user  or 'password' not in auth_user:
        response = {'message': 'missing key in post body'}
        return jsonify(response), 400

    username = auth_user['username']
    password = auth_user['password']

    user_management = UserManagement()
    authorized = user_management.authenticate_user(
        username=username,
        password=password
    )
    if authorized:
        access_token = create_access_token(identity=username)
        refresh_token = create_refresh_token(identity=username)
        response = jsonify({'login': True})
        set_access_cookies(response, access_token,
                           max_age=conf.JWT_ACCESS_TOKEN_EXPIRES)
        set_refresh_cookies(response, refresh_token,
                            max_age=conf.JWT_REFRESH_TOKEN_EXPIRES)
        return response, 200
    else:
        msg = 'authentication failed for user %s'%(auth_user['username'])
        response = {'message': msg}
        return jsonify(response), 401

@user_management.route('/service/user/logout', methods=['POST'])
def user_logout():
    """Logs the user out and deletes the JWT cookie from the server. """
    response = jsonify({'logout': True})
    unset_jwt_cookies(response)
    return response, 200

@user_management.route('/service/user/refresh', methods=['GET'])
@jwt_refresh_token_required
def user_refresh():
    """ Creates a refreshed access token for the user """
    username = get_jwt_identity()
    access_token = create_access_token(identity=username)
    response = jsonify({'refresh': True})
    set_access_cookies(response, access_token,
                       max_age=conf.JWT_ACCESS_TOKEN_EXPIRES)
    return response, 200

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
        modules = [x for x in user['modules'] if x in conf.AVAILABLE_MODULES]
        user['modules'] = modules
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
    # Only and admin can reset a password
    jwt_user = get_jwt_identity()
    admin_user = user_management.get_user(jwt_user)
    if admin_user['role'] != 'admin':
        response = {'message': 'only admins can reset password'}
        return jsonify(response), 403
    else:
        # Check the request body
        if 'username' not in request.json:
            response = {'message': 'username required in post body'}
            return jsonify(response), 400

        # Generate a password and post the update to the datase
        username = request.json['username']
        password = user_management.generate_password()
        user_management.update_password(username, password)
        response = {
            'message': 'role updated for %s'%(username),
            'password': password
        }
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
