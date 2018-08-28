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

    def run(self, test=False):
        """ Runs the data load process """
        last_event_date = self.database.last_event_date()
        if last_event_date:
            self.logger.info('Loading events starting at %s'%(last_event_date))
            start = str(last_event_date)[:10]
        else:
            self.logger.info('Loading events from the first available event')
            start = None
        events = self.eventbrite.get_events(start=start)

        num_events = events['pagination']['object_count']
        if num_events > 0:
            self.logger.info('There are %s events to process'%(num_events))
        else:
            self.logger.info('There are not next events. Exiting')
            return

        more_events = True
        while more_events:
            for event in events['events']:
                if not event:
                    continue
                msg = "Loading information for %s"%(event['name']['text'])
                self.logger.info(msg)
                # Load the event into the database. Delete the current
                # entry in order to maintain the unique index
                event_id = event['id']
                if not test:
                    self.database.delete_item('events', event_id)
                    self.load_event(event)

                # Load the attendee and order infomation
                attendees = self.eventbrite.get_attendees(event_id)
                more_attendees = True
                while more_attendees:
                    if not attendees:
                        break
                    for attendee in attendees['attendees']:
                        if not attendee:
                            continue
                        if not test:
                            self.database.delete_item(
                                'attendees',
                                attendee['id'],
                                {'event_id': event_id}
                            )
                            self.load_attendee(attendee)

                        # Load the order information
                        order_id = attendee['order_id']
                        order = self.eventbrite.get_order(order_id)
                        if not test:
                            self.database.delete_item('orders', order_id)
                            if order:
                                self.load_order(order)
                        else:
                            break
                    
                    if test or not attendees['pagination']['has_more_items']:
                        more_attendees = False
                        break
                    else:
                        page = attendees['pagination']['page_number'] + 1
                        attendees = self.eventbrite.get_attendees(event_id, page)
    
            if test or not events['pagination']['has_more_items']:
                more_events = False
                break
            else:
                page = events['pagination']['page_number'] + 1
                self.logger.info('\n Process pages %s of events \n'%(page))
                events = self.eventbrite.get_attendees(event_id, page)

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
        if 'email' in profile:
            attendee_['email'] = profile['email']
        else:
            attendee_['email'] = None

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


