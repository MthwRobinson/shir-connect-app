""" Flask app for the TRS Dashboard backend """
from flask import Flask, jsonify
from flask_jwt_simple import JWTManager, jwt_required, get_jwt_identity

import trs_dashboard.configuration as conf
from trs_dashboard.services.events import events
from trs_dashboard.services.user_management import user_management

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = conf.JWT_SECRET_KEY
app.config['JWT_EXPIRATION_DELTA'] = conf.JWT_EXPIRATION_DELTA
app.register_blueprint(user_management)
app.register_blueprint(events)
jwt = JWTManager(app)

@app.route('/service/test', methods=['GET'])
@jwt_required
def test():
    """ Tests to make sure the flask app is working """
    return jsonify({
        'status': 'success',
        'message': 'Hello, friend! My name is %s :)'%(
            get_jwt_identity()
        ),
        'name': get_jwt_identity()
    })
