"""
REST endpoints for the map geometries
A user must be authenticated
Includes:
    1. Flask route with /map path
    2. MapGeometries class for database calls
"""
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity

from shir_connect.database.database import Database
from shir_connect.database.map_geometries import MapGeometries
import shir_connect.configuration as conf
from shir_connect.services.utils import validate_inputs, log_request

map_geometries = Blueprint('map_geometries', __name__)

@map_geometries.route('/service/map/authorize', methods=['GET'])
@jwt_required
def map_authorize():
    """ Checks whether the users is authorized to view the map """
    database = Database()
    jwt_user = get_jwt_identity()
    user = database.get_item('users', jwt_user)

    authorized = conf.MAP_GROUP in user['modules']
    log_request(request, jwt_user, authorized)

    if not authorized:
        response = {'message': '%s does not have access the map'%(jwt_user)}
        return jsonify(response), 403
    else:
        response = {'message': '%s is authorized to view the map'%(jwt_user)}
        return jsonify(response), 200

@map_geometries.route('/service/map/geometry/<zipcode>', methods=['GET'])
@jwt_required
@validate_inputs(fields={'zipcode': {'type': 'int'}})
def geometry(zipcode):
    """ Retrieves a zip code geometry from the database """
    map_geometries = MapGeometries()
    # Make sure the user has access to the module
    jwt_user = get_jwt_identity()
    user = map_geometries.database.get_item('users', jwt_user)

    authorized = conf.MAP_GROUP in user['modules']
    log_request(request, jwt_user, authorized)

    if not authorized:
        response = {'message': '%s does not have access to the map'%(jwt_user)}
        return jsonify(response), 403

    layer = map_geometries.get_geometry(zipcode)
    return jsonify(layer)

@map_geometries.route('/service/map/geometries', methods=['GET'])
@jwt_required
def geometries():
    """ Retrieves all of the geometries for the map """
    map_geometries = MapGeometries()
    # Make sure the user has access to the module
    jwt_user = get_jwt_identity()
    user = map_geometries.database.get_item('users', jwt_user)

    authorized = conf.MAP_GROUP in user['modules']
    log_request(request, jwt_user, authorized)

    if not authorized:
        response = {'message': '%s does not have access to the map'%(jwt_user)}
        return jsonify(response), 403

    layers = map_geometries.get_geometries()
    return jsonify(layers)

@map_geometries.route('/service/map/zipcodes', methods=['GET'])
@jwt_required
def map_zip_codes():
    """ Retrieves a list of zip codes """
    map_geometries = MapGeometries()
    # Make sure the user has access to the module
    jwt_user = get_jwt_identity()
    user = map_geometries.database.get_item('users', jwt_user)

    authorized = conf.MAP_GROUP in user['modules']
    log_request(request, jwt_user, authorized)

    if not authorized:
        response = {'message': '%s does not have access to the map'%(jwt_user)}
        return jsonify(response), 403

    event_category = request.args.get('event_category')
    zip_codes = map_geometries.get_zip_codes(event_category=event_category)
    return jsonify(zip_codes)

@map_geometries.route('/service/map/default', methods=['GET'])
@jwt_required
def map_default():
    """ Returns the default location for the map. This location is
    user for the following purposes:

    1. It is used to center the event map
    2. For events with a null location, the default location is
        plotted on the map.
    """
    return jsonify(conf.DEFAULT_LOCATION)

@map_geometries.route('/service/map/event_options', methods=['GET'])
@jwt_required
def map_event_options():
    """Returns the event options for filtering on the map."""
    return jsonify(conf.MAP_EVENT_OPTIONS)
