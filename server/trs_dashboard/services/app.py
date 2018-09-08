""" Flask app for the TRS Dashboard backend """
from flask import Flask, jsonify

from trs_dashboard.services.user_management import user_management

app = Flask(__name__)
app.register_blueprint(user_management)

@app.route('/service/test', methods=['GET'])
def test():
    """ Tests to make sure the flask app is working """
    return jsonify({
        'status': 'success',
        'message': 'Hello, friend! :)'
    })
