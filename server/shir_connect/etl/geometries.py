"""
Function for downloading and zip code KML files
and converting them to GeoJSON
"""
import json
import os

import kml2geojson
import pandas as pd
import requests
from uszipcode import SearchEngine

from shir_connect.database.database import Database

class Geometries(object):
    """ Class for parsing and loading geojson files """
    def __init__(self, database=None):
        self.database = Database() if not database else database
        self.path = os.path.dirname(os.path.realpath(__file__))
        self.url = 'https://www.zip-codes.com/cache/kml-zip/'
        self.search = SearchEngine(simple_zipcode=True)

    def get_kml(self, zip_code):
        """ Pulls the KML file for a zip code """
        url = self.url + '%s.kml'%(zip_code)
        response = requests.get(url)
        if response.status_code == 200:
            return response.text
        else:
            return None

    def missing_zip_codes(self):
        """ Pulls a list of distinct zip codes from the database """
        sql = """
            SELECT DISTINCT postal_code
            FROM(
                SELECT DISTINCT postal_code
                FROM {schema}.venues
                UNION ALL
                SELECT DISTINCT postal_code
                FROM {schema}.members_view
            ) x
            WHERE postal_code NOT IN (
                SELECT id as postal_code
                FROM {schema}.geometries
            )
        """.format(schema=self.database.schema)
        df = pd.read_sql(sql, self.database.connection)
        zip_codes = [x for x in df['postal_code']]
        return zip_codes

    def load_zip_code(self, zip_code):
        """ Pulls a zip code and loads it into the database """
        # Fetch the KML file from the resource
        kml = self.get_kml(zip_code)
        if not kml:
            return

        filename = self.path + '/temp/%s.kml'%(zip_code)
        with open(filename, 'w') as f:
            f.write(kml)

        # Convert the KML file to GeoJSON
        kml2geojson.main.convert(filename, self.path+'/temp')

        # Load the file into the database
        geo_filename = self.path + '/temp/%s.geojson'%(zip_code)
        with open(geo_filename, 'r') as f:
            geo_json = json.load(f)
        row = {'id': zip_code, 'geometry': json.dumps(geo_json)}
        self.database.load_item(row, 'geometries')

        # Delete the temporary files
        os.remove(filename)
        os.remove(geo_filename)

    def load_locations(self):
        """Loads any missing location names into the database."""
        missing = self.missing_locations()
        for zip_code in missing:
            data = self.get_zipcode_data(zip_code)
            if data:
                city = "'{}'".format(data['major_city'].replace("'", ""))
                self.database.update_column('geometries', item_id=zip_code,
                                             column='city', value=city)

                county = "'{}'".format(data['county'].replace("'", ""))
                self.database.update_column('geometries', item_id=zip_code,
                                            column='county', value=county)

                state = "'{}'".format(data['state'])
                self.database.update_column('geometries', item_id=zip_code,
                                            column='region', value=state)

    def missing_locations(self):
        """Pulls a list of zip codes for which we don't have
        a city and county name."""
        sql = """
            SELECT DISTINCT id
            FROM {schema}.geometries
        """.format(schema=self.database.schema)
            #WHERE city IS NULL or county IS NULL
        df = pd.read_sql(sql, self.database.connection)
        zip_codes = self.database.to_json(df)
        return [x['id'] for x in zip_codes]

    def get_zipcode_data(self, zipcode):
        """Pulls the city and county name for the specified zipcode."""
        results = self.search.by_zipcode(zipcode)
        if results.zipcode:
            zipcode_data = results.to_dict()
        else:
            zipcode_data = None
        return zipcode_data
