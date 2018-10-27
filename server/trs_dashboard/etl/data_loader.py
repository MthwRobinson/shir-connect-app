""" ETL process for loading data into Postgres """
from copy import deepcopy
import datetime
import logging
import time

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
            today = datetime.datetime.now() - datetime.timedelta(days=1)
            first_event = min(today, last_event_date)
            start = str(first_event)[:10]
        else:
            self.logger.info('Loading events from the first available event')
            start = None
        events = self.get_events(start=start, page=1)

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

                # Load the venue, if it does not already
                # appear in the database
                venue_id = event['venue_id']
                venue_ = self.database.get_item('venues', venue_id)
                if venue_id and not venue_:
                    venue = self.get_venue(venue_id)
                    if not test:
                        self.load_venue(venue)

                attendees = self.get_attendees(event_id, page=1)
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

                    if test or not attendees['pagination']['has_more_items']:
                        more_attendees = False
                        break
                    else:
                        page = attendees['pagination']['page_number'] + 1
                        attendees = self.get_attendees(event_id, page)
                # Sleep to avoid the Eventbrite rate limit
                if test:
                    break
                else:
                    time.sleep(60)

            if events['pagination']['has_more_items']:
                more_events = False
                break
            else:
                page = events['pagination']['page_number'] + 1
                msg = 'Pulling events on page %s'%(page)
                self.logger.info(msg)
                events = self.get_events(start, page)

        # Refresh the materialized views with the new data
        self.database.refresh_views()

    def get_events(self, start, page=1):
        """ 
        Pulls events from eventbrite and sleeps if the rate limit
        has been exceeded
        """
        events = self.eventbrite.get_events(start=start, page=page)
        if not events:
            # Sleep until eventbrite resets
            self.logger.info('Rate limit exceed. Sleeping 30 mins')
            time.sleep(3600)
            events = self.eventbrite.get_events(start=start, page=page)
        return events

    def get_attendees(self, event_id, page=1):
        """
        Pulls attendees from eventbrite and sleeps if the rate limit
        has been exceeded
        """
        attendees = self.eventbrite.get_attendees(event_id, page)
        if not attendees:
            # If events comes back as none, sleep until the 
            # Eventbrite rate limit resets
            self.logger.info('Rate limit exceed. Sleeping 30 mins')
            time.sleep(3600)
            attendees = self.eventbrite.get_attendees(event_id, page)
        return attendees

    def get_venue(self, venue_id, page=1):
        """
        Pull a venue and sleeps if the rate limit
        has been exceeded
        """
        venue = self.eventbrite.get_venue(venue_id, page)
        if not venue:
            self.logger.info('Rate limit exceed. Sleeping 30 mins')
            time.sleep(3600)
            venue = self.eventbrite.get_venue(event_id, page)
        return venue

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
        if 'name' in profile:
            attendee_['name'] = profile['name']
        if 'first_name' in profile:
            attendee_['first_name'] = profile['first_name']
        if 'last_name' in profile:
            attendee_['last_name'] = profile['last_name']
        if 'email' in profile:
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

    def load_venue(self, venue):
        """ Loads a venue into the database """
        venue_ = deepcopy(venue)

        for key in venue_['address']:
            val = venue_['address'][key]
            venue_[key] = val

        venue_['latitude'] = float(venue_['latitude'])
        venue_['longitude'] = float(venue_['longitude'])
        self.database.load_item(venue_, 'venues')



