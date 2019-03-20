""" Connects to the Eventbrite API """
import json
import logging
import urllib

import daiquiri
import requests

import shir_connect.configuration as conf

class Eventbrite(object):
    """ Makes Eventbrite REST calls using an OAUTH token """
    def __init__(self):
        daiquiri.setup(level=logging.INFO)
        self.logger = daiquiri.getLogger(__name__)

        self.token = conf.EVENTBRITE_OAUTH
        self.url = 'https://www.eventbriteapi.com/v3'

    def get_token_info(self):
        """ Returns metadata about the account associated with the token """
        params = urllib.parse.urlencode({'token': self.token})
        url = self.url + '/users/me/?' + params
        response = requests.get(url)
        return response

    def get_events(self, org_id, start=None, page=1):
        """ Pulls a list of events basd on id """
        url = self.url + '/organizers/%s/events/'%(org_id)

        # Add the query parameters
        param_dict = {'token': self.token, 'page': page}
        if start:
            date = start + 'T0:00:00'
            param_dict['start_date.range_start'] = date
        params = urllib.parse.urlencode(param_dict)
        url += '?' + params
        
        # Make and parse the request
        response = requests.get(url)
        if response.status_code != 200:
            code = response.status_code
            msg = 'Response had status code: %s'%(code)
            self.logger.warning(msg)
            return None
        else:
            events = json.loads(response.text)
            return events 

    def get_event(self, event_id, page=1):
        """ Returns an event based on an id """
        params = urllib.parse.urlencode({
            'token': self.token, 
            'page': page
        })
        url = self.url + '/events/%s'%(event_id)
        url += '?' + params
        response = requests.get(url)
        if response.status_code != 200:
            code = response.status_code
            msg = 'Response had status code: %s'%(code)
            self.logger.warning(msg)
            return None
        else:
            event = json.loads(response.text)
            return event
    
    def get_attendees(self, event_id, page=1):
        """ Returns the attendees of an event based on an id """
        params = urllib.parse.urlencode({
            'token': self.token, 
            'page': page
        })
        url = self.url + '/events/%s/attendees'%(event_id)
        url += '?' + params
        response = requests.get(url)
        if response.status_code != 200:
            code = response.status_code
            msg = 'Response had status code: %s'%(code)
            self.logger.warning(msg)
            return None
        else:
            attendees = json.loads(response.text)
            return attendees

    def get_order(self, order_id, page=1):
        """ Returns metadata about an order """
        params = urllib.parse.urlencode({
            'token': self.token, 
            'page': page
        })
        url = self.url + '/orders/%s'%(order_id)
        url += '?' + params
        response = requests.get(url)
        if response.status_code != 200:
            code = response.status_code
            msg = 'Response had status code: %s'%(code)
            self.logger.warning(msg)
            return None
        else:
            order = json.loads(response.text)
            return order

    def get_venue(self, venue_id, page=1):
        """ Returns the metadata for a venue """
        params = urllib.parse.urlencode({
            'token': self.token, 
            'page': page
        })
        url = self.url + '/venues/%s'%(venue_id)
        url += '?' + params
        response = requests.get(url)
        if response.status_code != 200:
            code = response.status_code
            msg = 'Response had status code: %s'%(code)
            self.logger.warning(msg)
            return None
        else:
            venue = json.loads(response.text)
            return venue
