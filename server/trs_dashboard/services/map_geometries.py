"""
REST endpoints for the map geometries
A user must be authenticated
Includes:
    1. Flask route with /map path
    2. MapGeometries class for database calls
"""
from flask import Blueprint, abort, jsonify, request
from flask_jwt_simple import jwt_required
import pandas as pd

from trs_dashboard.database.database import Database

map_geometries = Blueprint('map_geometries', __name__)

@map_geometries.route('/service/map/geometry/<zipcode>', methods=['GET'])
@jwt_required
def geometry(zipcode):
    """ Retrieves a zip code geometry from the database """
    map_geometries = MapGeometries()
    layer = map_geometries.get_geometry(zipcode)
    return jsonify(layer)

@map_geometries.route('/service/map/geometries', methods=['GET'])
@jwt_required
def geometries():
    """ Retrieves all of the geometries for the map """
    map_geometries = MapGeometries()
    limit = request.args.get('limit')
    if not limit:
        limit = None
    layers = map_geometries.get_geometries(limit=limit)
    return jsonify(layers)

@map_geometries.route('/service/map/zipcodes', methods=['GET'])
@jwt_required
def zip_codes():
    """ Retrieves a list of zip codes """
    map_geometries = MapGeometries()
    zip_codes = map_geometries.get_zip_codes()
    return jsonify(zip_codes)

class MapGeometries(object):
    """ Class that handles geometries for the map """
    def __init__(self):
        self.database = Database()

    def get_geometry(self, zip_code):
        """ Constructs the geometry for the specified zip code """
        geometry = self.database.get_item('geometries', zip_code)
        colors = self.database.get_item('shape_colors', zip_code)
        if colors:
            red = int(colors['red'])
            blue = int(colors['blue'])
            events = int(colors['events'])
            members = int(colors['residents'])
        else:
            red = 0; blue = 0; events = 0; members = 0;
        layer = self.build_layer(geometry, red, blue, members, events)
        return layer

    def get_geometries(self, limit=None):
        """ Returns all of the geometries with their colors """
        sql = """
            SELECT
                a.id as postal_code, 
                geometry, 
                residents, 
                red, 
                events, 
                blue
            FROM {schema}.geometries a 
            INNER JOIN {schema}.shape_colors b
            ON a.id = b.id
            WHERE a.id IS NOT NULL
        """.format(schema=self.database.schema)
        if limit:
            sql += " LIMIT %s "%(limit)
        df = pd.read_sql(sql, self.database.connection)
        
        layers = {}
        for i in df.index:
            geometry = dict(df.loc[i])
            postal_code = geometry['postal_code']
            geo = {
                'geometry': geometry['geometry'], 
                'id': geometry['postal_code']
            }
            red = geometry['red']
            blue = geometry['blue']
            members = geometry['residents']
            events = geometry['events']
            layer = self.build_layer(geo, red, blue, members, events)
            layers[postal_code] = layer
        return layers

    def build_layer(self, geometry, red, blue, members, events):
        """ Builds the map layer with the correct colors """
        geojson = geometry['geometry']
        geojson['features'][0]['properties'] = {
            'description': """
                <strong>Zip Code: {zip_code}</strong>
                <ul>
                    <li>Members: {members}</li>
                    <li>Events: {events}</li>
                </ul>
            """.format(
                zip_code=geometry['id'],
                members=members,
                events=events
            )
        }
        layer = {
            'id': geometry['id'],
            'type': 'fill',
            'source' : {
                'type': 'geojson',
                'data': geojson
            },
            'paint': {
                'fill-color': 'rgb(%s, 256, %s)'%(red,blue),
                'fill-opacity': 0.6,
                'fill-outline-color': 'rgb(0, 0, 0)'
            }
        }
        return layer

    def get_zip_codes(self):
        """ 
        Pulls a list of zip codes that have at least
        one event and at least one member 
        """
        sql = """
            SELECT DISTINCT postal_code
            FROM (
                SELECT DISTINCT postal_code
                FROM {schema}.members_view
                UNION ALL
                SELECT DISTINCT postal_code
                FROM {schema}.venues
            ) a
            INNER JOIN {schema}.geometries b
            ON a.postal_code = b.id
        """.format(schema=self.database.schema)
        df = pd.read_sql(sql, self.database.connection)
        if len(df) > 0:
            response = [str(x) for x in df['postal_code']]
        else:
            response = []
        return response

