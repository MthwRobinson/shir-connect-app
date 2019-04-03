""" Loads the geometries that are used on the event map. """
import pandas as pd

from shir_connect.database.database import Database

class MapGeometries:
    """ Class that handles geometries for the map """
    def __init__(self, database=None):
        self.database = database if database else Database()

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
            red = 0
            blue = 0
            events = 0
            members = 0
        layer = build_layer(geometry, red, blue, members, events)
        return layer

    def get_geometries(self):
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
        df = pd.read_sql(sql, self.database.connection)

        layers = {}
        for i in df.index:
            geometry = dict(df.loc[i])
            postal_code = geometry['postal_code']
            geo = {
                'geometry': geometry['geometry'],
                'id': geometry['postal_code']
            }
            if len(geo['geometry']['features']) == 0:
                continue
            red = int(geometry['red'])
            blue = int(geometry['blue'])
            members = int(geometry['residents'])
            events = int(geometry['events'])
            layer = build_layer(geo, red, blue, members, events)
            layers[postal_code] = layer
        return layers

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

def build_layer(geometry, red, blue, members, events):
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
            'fill-color': 'rgb(%s, 256, %s)'%(red, blue),
            'fill-opacity': 0.6,
            'fill-outline-color': 'rgb(0, 0, 0)'
        }
    }
    return layer
