"""Object for interacting with the Little Green Light API.
Authenticates with the API using a token in the API header."""
import json
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

    def get(self, endpoint, params=None, full_url=False, return_dict=False):
        """Makes a GET requests to the LGL API and using the
        token to authenticate

        Params
        ------
        endpoint : str
            the REST end point to fetch
        params : dict
            a dictionary of query parameters for the request
        full_url : boolean
            if True, the get request will assume enpoint is the
            full endpoint, otherwise the base_url prefix will be added
        return_dict : boolean
            if True, returns a dictionary instead of a response object

        Returns
        -------
        response : requests.Response
        """
        headers  = {'Authorization': 'Bearer {}'.format(self.token)}
        url = self.url + endpoint if not full_url else endpoint
        if params:
            url += '?' + urllib.parse.urlencode(params)
        response = requests.get(url, headers=headers)

        if return_dict:
            return json.loads(response.text)
        else:
            return response

    def get_constituents(self, limit=25, offset=0, traverse=True):
        """Pulls a list of constituents from the LGL API

        Params
        ------
        limit : int
            the number of constituents to return on each call
        offset : int
            the entry to start on
        traverse : boolean
            if True, traverses through the paginated results

        Returns
        -------
        constituents : list
        """
        params = {'limit': limit, 'offset': offset}
        if traverse:
            return self._traverse_results('/constituents', params)
        else:
            response = self.get('/constituents', params, return_dict=True)
            return response['items']

    def get_addresses(self, constituent_id, limit=25, offset=0, traverse=True):
        """Pulls the address for a given constituent id

        Params
        ------
        constituent_id : str
            the id of the constituent whose address we want
        limit : int
            the number of addresses to return on each call
        offset : int
            the entry to start on
        traverse : boolean
            if True, traverses through the paginated results

        Returns
        -------
        addresses : list
        """
        endpoint = 'constituents/{}/street_addresses'.format(constituent_id)
        params = {'limit': limit, 'offset': offset}
        if traverse:
            return self._traverse_results(endpoint, params)
        else:
            response = self.get(endpoint, params, return_dict=True)
            return response['items']

    def get_email_addresses(self, constituent_id, limit=25,
                            offset=0, traverse=True):
        """Pulls the address for a given constituent id

        Params
        ------
        constituent_id : str
            the id of the constituent whose address we want
        limit : int
            the number of addresses to return on each call
        offset : int
            the entry to start on
        traverse : boolean
            if True, traverses through the paginated results

        Returns
        -------
        addresses : list
        """
        endpoint = 'constituents/{}/email_addresses'.format(constituent_id)
        params = {'limit': limit, 'offset': offset}
        if traverse:
            return self._traverse_results(endpoint, params)
        else:
            response = self.get(endpoint, params, return_dict=True)
            return response['items']

    def _traverse_results(self, endpoint, params=None):
        """Traverses paginated results and collects the items from
        each page into a single list."""
        items = []
        response = self.get(endpoint, params, return_dict=True)
        done_traversing = False
        while not done_traversing:
            items += response['items']
            if 'next_link' in response:
                next_link = response['next_link']
            else:
                next_link = None
            if not next_link:
                done_traversing = True
            else:
                response = self.get(next_link, full_url=True, return_dict=True)
        return items
