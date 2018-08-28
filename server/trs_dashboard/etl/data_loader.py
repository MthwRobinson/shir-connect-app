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



