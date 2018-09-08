""" Flask app for the TRS Dashboard backend """
from flask import Flask, abort, jsonify, request

from trs_dashboard.services.user_management import UserManagement

app = Flask(__name__)

@app.route('/service/test', methods=['GET'])
def test():
    """ Tests to make sure the flask app is working """
    return jsonify({
        'status': 'success',
        'message': 'Hello, friend! :)'
    })

@app.route('/service/user/register', methods=['POST'])
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

@app.route('/service/user/authenticate', method=['POST']):
    """ Authenticates the user """
    pass

