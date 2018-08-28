""" ETL process for loading data into Postgres """
from copy import deepcopy
import datetime
import logging

import arrow
import daiquiri

from trs_dashboard.database.database import Database
from trs_dashboard.etl.eventbrite import Eventbrite

class DataLoader(object):
    """ Loads data from multiple sources into Postgres """
    def __init__(self):
        daiquiri.setup(level=logging.INFO)
        self.logger = daiquiri.getLogger(__name__)

        self.database = Database()
        self.eventbrite = Eventbrite()

    def load_event(self, event):
        """ Loads an event into the database """
        event_ = deepcopy(event)

        start = arrow.get(event_['start']['utc']).datetime
        event_['start_datetime'] = start

        end = arrow.get(event_['end']['utc']).datetime
        event_['end_datetime'] = end

        description = event_['description']['text']
        event_['description'] = description

        name = event_['name']['text']
        event_['name'] = name

        event_['load_datetime'] = datetime.datetime.utcnow()
        self.database.load_item(event_, 'events')

    def load_attendee(self, attendee):
        """ Loads an attendee into the database """
        attendee_ = deepcopy(attendee)

        profile = attendee_['profile']
        attendee_['name'] = profile['name']
        attendee_['first_name'] = profile['first_name']
        attendee_['last_name'] = profile['last_name']
        attendee_['email'] = profile['email']

        cost = attendee_['costs']['gross']['major_value']
        attendee_['cost'] = float(cost)

        attendee_['load_datetime'] = datetime.datetime.utcnow()
        self.database.load_item(attendee_, 'attendees')

    def load_order(self, order):
        """ Loads an order into the database """
        order_ = deepcopy(order)

        cost = order_['costs']['gross']['major_value']
        order_['cost'] = float(cost)

        order_['load_datetime'] = datetime.datetime.utcnow()
        self.database.load_item(order_, 'orders')



