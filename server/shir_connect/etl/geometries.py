"""
Function for downloading and zip code KML files
and converting them to GeoJSON
"""
import logging
import json
import os
import time

import daiquiri
import kml2geojson
import pandas as pd
import requests
from uszipcode import SearchEngine

from shir_connect.database.database import Database

class Geometries(object):
    """ Class for parsing and loading geojson files """
    def __init__(self, database=None):
        daiquiri.setup(level=logging.INFO)
        self.logger = daiquiri.getLogger(__name__)

        self.database = Database(database=database)
        self.path = os.path.dirname(os.path.realpath(__file__))
        self.url = 'https://www.zip-codes.com/cache/kml-zip/'
        self.search = SearchEngine(simple_zipcode=True)
        self.zip_code_cache= {}

    def load_all_zip_codes(self):
        """Loads all zipcodes geometries into the database. Pauses five
        seconds betwen loading each zipcode to avoid overwhelming the
        site we download the geometries from."""
        valid_zip_codes = self.get_all_zip_codes()
        for code in valid_zip_codes:
            try:
                self.logger.info("Loading geometry for {}".format(code))
                self.load_zip_code(code)
            except:
                self.logger.warning('Geojson load failed for {}'.format(code))
            time.sleep(5)

    def get_kml(self, zip_code):
        """ Pulls the KML file for a zip code """
        url = self.url + '%s.kml'%(zip_code)
        response = requests.get(url)
        if response.status_code == 200:
            return response.text
        else:
            return None

    def get_all_zip_codes(self):
        """Creates a list of valid zip codes by checking them
        against the US zip code search object."""
        possible_zip_codes = [str(i).rjust(5, '0') for i in range(20000, 20050)]
        valid_zip_codes = []
        for code in possible_zip_codes:
            results = self.get_zipcode_data(code)
            if results and results['zipcode'] != None:
                valid_zip_codes.append(code)

        return valid_zip_codes

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

        zipcode_data = self.get_zipcode_data(zip_code)
        row = {'id': zip_code,
                'geometry': json.dumps(geo_json),
                'city': zipcode_data['major_city'],
                'county': zipcode_data['county'],
                'region': zipcode_data['state']}
        self.database.delete_item('geometries', zip_code)
        self.database.load_item(row, 'geometries')

        # Delete the temporary files
        os.remove(filename)
        os.remove(geo_filename)

    def get_zipcode_data(self, zipcode):
        """Pulls the city and county name for the specified zipcode."""
        if zipcode in self.zip_code_cache:
            return self.zip_code_cache[zipcode]
        else:
            results = self.search.by_zipcode(zipcode)
            if results.zipcode:
                zipcode_data = results.to_dict()
            else:
                zipcode_data = None
            # Cache city and state information for later so we don't
            # have to search against the search engine again
            self.zip_code_cache[zipcode] = zipcode_data
            return zipcode_data
