"""Object for interacting with the Little Green Light API.
Authenticates with the API using a token in the API header."""
import logging
import urllib

import daiquiri
import requests

import shir_connect.configuration as conf

class LittleGreenLight:
    """Makes REST calls to the Little Green Light API
    using an access token in the authorization header."""
    def __init__(self):
        daiquiri.setup(level=logging.INFO)
        self.logger = daiquiri.getLogger(__name__)

        self.token = conf.LGL_TOKEN
        self.url = 'https://api.littlegreenlight.com/api/v1'
        self.headers = {'Authorization': 'Bearer {}'.format(self.token)}

    def get(self, endpoint, params=None):
        """Makes a GET requests to the LGL API and using the
        token to authenticate

        Params
        ------
        endpoint : str
        the REST end point to fetch

        Returns
        -------
        response : requests.Response
        """
        headers  = {'Authorization': 'Bearer {}'.format(self.token)}
        url = self.url + endpoint
        if params:
            url += '?' + urllib.parse.urlencode(params)
        response = requests.get(url, headers=headers)
        return response


