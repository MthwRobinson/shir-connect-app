""" Flask app for the TRS Dashboard backend """
from flask import Flask, jsonify
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity

import shir_connect.configuration as conf
from shir_connect.services.events import events
from shir_connect.services.trends import trends
from shir_connect.services.map_geometries import map_geometries
from shir_connect.services.members import members
import shir_connect.services.utils as utils
from shir_connect.services.user_management import user_management

app = Flask(__name__)

# Set JSON web token configurations
app.config['JWT_SECRET_KEY'] = conf.JWT_SECRET_KEY
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = conf.JWT_ACCESS_TOKEN_EXPIRES
app.config['JWT_REFRESH_TOKEN_EXPIRES'] = conf.JWT_REFRESH_TOKEN_EXPIRES

# Register end points with the appp
app.register_blueprint(events)
app.register_blueprint(trends)
app.register_blueprint(map_geometries)
app.register_blueprint(members)
app.register_blueprint(user_management)

jwt = JWTManager(app)

@app.route('/service/test/<name>')
@utils.validate_inputs(name)
def test_route():
    """ This route is for use in the unit tests, and also to verify
    that the REST platform is working without connecting to the 
    database and/or having to pass in credentials. """
    return jsonify({'message': 'hello world!'}), 200
