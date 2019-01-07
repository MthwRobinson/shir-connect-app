""" Flask app for the TRS Dashboard backend """
from flask import Flask, jsonify
from flask_jwt_simple import JWTManager, jwt_required, get_jwt_identity

import trs_dashboard.configuration as conf
from trs_dashboard.services.events import events
from trs_dashboard.services.trends import trends
from trs_dashboard.services.map_geometries import map_geometries
from trs_dashboard.services.members import members
from trs_dashboard.services.user_management import user_management

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = conf.JWT_SECRET_KEY
app.config['JWT_EXPIRATION_DELTA'] = conf.JWT_EXPIRATION_DELTA
app.register_blueprint(events)
app.register_blueprint(trends)
app.register_blueprint(map_geometries)
app.register_blueprint(members)
app.register_blueprint(user_management)
jwt = JWTManager(app)
