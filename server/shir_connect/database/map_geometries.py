""" Loads the geometries that are used on the event map. """
import pandas as pd
import numpy as np
from scipy import stats

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
            SELECT a.id as postal_code, geometry
            FROM {schema}.geometries a
            INNER JOIN (
                SELECT postal_code
                FROM(
                    SELECT COUNT(DISTINCT id) as total,  postal_code
                    FROM (
                        SELECT id, postal_code
                        FROM {schema}.members_view
                        UNION ALL
                        SELECT id, postal_code
                        FROM {schema}.event_aggregates
                    ) events
                    GROUP BY postal_code
                ) places
                WHERE total >= 5
            ) b
            ON a.id = b.postal_code
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

    def get_zip_codes(self, event_category=None):
        """Pulls a list of zip codes that have at least
        one event and at least one member."""
        members = self.get_member_counts(event_category)
        events = self.get_event_counts(event_category)
        results = consolidate_results(members, events)

        return results

    def get_event_counts(self, event_category=None):
        """Gets a count of events grouped by zip code."""
        if event_category:
            category_condition = " AND lower(a.name) "
            category_condition += "like '%{}%' ".format(event_category.lower())
        else:
            category_condition = ""

        sql = """
            SELECT COUNT(DISTINCT a.id) AS total, postal_code
            FROM {schema}.events a
            INNER JOIN {schema}.venues b
            ON a.venue_id = b.id
            WHERE postal_code IS NOT NULL
            {category_condition}
            GROUP BY postal_code
        """.format(schema=self.database.schema,
                   category_condition=category_condition)
        df = pd.read_sql(sql, self.database.connection)
        return df

    def get_member_counts(self, event_category=None):
        """Gets a count of members grouped by zip code."""
        if event_category:
            category_condition = " AND lower(e.name) "
            category_condition += "like '%{}%' ".format(event_category.lower())
        else:
            category_condition = ""

        sql = """
            SELECT COUNT(DISTINCT a.id) AS total, postal_code
            FROM {schema}.members a
            INNER JOIN {schema}.participant_match b
            ON a.id = b.member_id
            INNER JOIN {schema}.attendee_to_participant c
            ON c.participant_id = b.id
            INNER JOIN {schema}.attendees d
            ON c.id = d.id
            INNER JOIN {schema}.events e
            ON e.id = d.event_id
            WHERE a.postal_code IS NOT NULL
            {category_condition}
            GROUP BY postal_code
        """.format(schema=self.database.schema,
                   category_condition=category_condition)
        df = pd.read_sql(sql, self.database.connection)
        return df


def consolidate_results(members, events):
    """Consolidates the results of the counts queries and finds the min
    and max counts, excluding the default location. The default location
    is excluded by a large number of events take place there."""
    df = members.merge(events, how='outer', on='postal_code', suffixes=['_members', '_events'])
    df = df.fillna(0)
    df_orig = df.copy()

    default = str(conf.DEFAULT_LOCATION['postal_code'])
    df = df[df['postal_code'] != default]

    df['pct_members'] = df['total_members'] / df['total_members'].sum()
    df['pct_events'] = df['total_events'] / df['total_events'].sum()
    df['pct_diff'] = df['pct_members'] - df['pct_events']

    df['percentile'] = [stats.percentileofscore(df['pct_diff'], x, 'strict')
                        for x in df['pct_diff']]
    df['color'] = 256 - (2.56 * df['percentile'])

    df['color'] = df['color'].astype(float)
    df['total_members'] = df['total_members'].astype(float)
    df['total_events'] = df['total_events'].astype(float)

    df = df.append(df_orig.loc[df_orig['postal_code'] == default], sort=False)
    df = df.reset_index()

    results = {}
    for i in df.index:
        data = dict(df.loc[i])
        if data['postal_code'] == default:
            color = 256
        else:
            color = data['color']

        results[data['postal_code']] = {
            'total_members': data['total_members'],
            'total_events': data['total_events'],
            'color': color
        }

    return results

def build_layer(geometry):
    """Builds the map layer with the correct colors."""
    geojson = geometry['geometry']
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
            'fill-outline-color': 'rgb(70, 70, 70)'
        }
    }
    return layer
