""" Connects to the Eventbrite API """
import requests
import urllib

import trs_dashboard.configuration as conf

class Eventbrite(object):
    """ Makes Eventbrite REST calls using an OAUTH token """
    def __init__(self):
        self.token = conf.EVENTBRITE_OAUTH
        self.url = 'https://www.eventbriteapi.com/v3'

    def get_token_info(self):
        """ Returns metadata about the account associated with the token """
        params = urllib.parse.urlencode({'token': self.token})
        url = self.url + '/users/me/?' + params
        response = requests.get(url)
        return response
