""" Loads the geometries that are used on the event map. """
import pandas as pd
import numpy as np

import shir_connect.configuration as conf
from shir_connect.database.database import Database

class MapGeometries:
    """ Class that handles geometries for the map """
    def __init__(self, database=None):
        self.database = database if database else Database()

    def get_geometry(self, zip_code):
        """ Constructs the geometry for the specified zip code """
        geometry = self.database.get_item('geometries', zip_code)
        layer = build_layer(geometry)
        return layer

    def get_geometries(self):
        """ Returns all of the geometries with their colors """
        sql = """
            SELECT id as postal_code, geometry
            FROM {schema}.geometries a
            WHERE id IS NOT NULL
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
            # Skip any geometries that don't have features
            if len(geo['geometry']['features']) == 0:
                continue
            layer = build_layer(geo)
            layers[postal_code] = layer
        return layers

    def get_zip_codes(self):
        """Pulls a list of zip codes that have at least
        one event and at least one member."""
        members = self.get_member_counts()
        events = self.get_event_counts()

        response = {}
        zip_codes = set(members.keys()).union(set(events.keys()))
        for zip_code in zip_codes:
            if zip_code in events:
                zip_events = events[zip_code]
            else:
                zip_events = {'count': 0.0, 'color': 0.0}

            if zip_code in members:
                zip_members = members[zip_code]
            else:
                zip_members = {'count': 0.0, 'color': 0.0}

            response[zip_code] = {'events': zip_events, 'members': zip_members}

        return response

    def get_event_counts(self):
        """Gets a count of events grouped by zip code."""
        sql = """
            SELECT COUNT(DISTINCT a.id) AS total, postal_code
            FROM {schema}.events a
            INNER JOIN {schema}.venues b
            ON a.venue_id = b.id
            WHERE postal_code IS NOT NULL
            GROUP BY postal_code
        """.format(schema=self.database.schema)
        df = pd.read_sql(sql, self.database.connection)
        results = consolidate_results(df)
        return results

    def get_member_counts(self):
        """Gets a count of members grouped by zip code."""
        sql = """
            SELECT COUNT(DISTINCT id) AS total, postal_code
            FROM {schema}.members
            WHERE postal_code IS NOT NULL
            GROUP BY postal_code
        """.format(schema=self.database.schema)
        df = pd.read_sql(sql, self.database.connection)
        results = consolidate_results(df)
        return results


def consolidate_results(df):
    """Consolidates the results of the counts queries and finds the min
    and max counts, excluding the default location. The default location
    is excluded by a large number of events take place there."""
    default = str(conf.DEFAULT_LOCATION['postal_code'])
    df_no_default = df[df['postal_code'] != default]
    max_count = df_no_default['total'].max()
    min_count = df_no_default['total'].min()
    df['color'] = layer_color(df['total'], min_count, max_count)

    df['color'] = df['color'].astype(float)
    df['total'] = df['total'].astype(float)

    results = {}
    for i in df.index:
        data = dict(df.loc[i])
        results[data['postal_code']] = {
            'count': data['total'],
            'color': data['color']
        }

    return results

@np.vectorize
def layer_color(count, min_count, max_count):
    """Determines the RGB color of the cell based on the count in the cell,
    the min count and the max count.

    Paramters
    ---------
    count: the count value in the area
    min_count: the minimum count in the data set
    max_count: the maximum count in the data set

    Returns
    -------
    color: float in [0, 256], the RGB value for the tile
    """
    if count > max_count:
        count = max_count
    adj_min = max(min_count, 1)

    numerator = np.log(count) - np.log(adj_min)
    denominator = np.log(max_count) - np.log(adj_min)

    if denominator > 0:
        normalized_color = min(numerator/denominator, 1)
    else:
        normalized_color = 1
    return 256-(256*normalized_color)

def build_layer(geometry):
    """Builds the map layer with the correct colors."""
    geojson = geometry['geometry']
    geojson['features'][0]['properties'] = {
        'description': """
            <strong>Zip Code: {zip_code}</strong>
            <ul>
                <li>Members: UPDATE ME</li>
                <li>Events: UPDATE ME</li>
            </ul>
        """.format(zip_code=geometry['id'])
    }
    layer = {
        'id': geometry['id'],
        'type': 'fill',
        'source' : {
            'type': 'geojson',
            'data': geojson
        },
        'paint': {
            'fill-color': 'rgb(0, 0, 0)',
            'fill-opacity': 0.6,
            'fill-outline-color': 'rgb(0, 0, 0)'
        }
    }
    return layer
