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
        geojson = geometry['geometry']
        geojson['features'][0]['properties'] = {
            'description': '<strong>%s</strong>'%(zip_code)
        }
        layer = {
            'id': zip_code,
            'type': 'fill',
            'source' : {
                'type': 'geojson',
                'data': geojson
            },
            'paint': {
                'fill-color': 'rgb(0, 255, 255)',
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

