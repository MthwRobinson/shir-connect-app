""" Methods for fetching events from the database. """
import datetime
import logging

import daiquiri
import pandas as pd
import numpy as np

import shir_connect.configuration as conf
from shir_connect.database.database import Database
from shir_connect.services.utils import demo_mode

class Events:
    """ Class that handles event database calls """
    def __init__(self, database=None):
        daiquiri.setup(level=logging.INFO)
        self.logger = daiquiri.getLogger(__name__)

        self.database = database if database else Database()

    def get_events(self, limit=None, page=None, order=None,
                   sort=None, q=None, where=[], fake=False):
        """ Fetches the most recent events from the database """
        limit = 25 if not limit else limit
        name_col = 'fake_name' if fake else 'name'
        query = (name_col, q) if q else None
        df = self.database.read_table('event_aggregates', limit=limit,
                                      page=page, order=order, sort=sort,
                                      query=query, where=where)
        count = self.database.count_rows('event_aggregates', query=query,
                                         where=where)

        pages = int((count/limit)) + 1
        events = self.database.to_json(df)
        if fake:
            for event in events:
                event['name'] = event['fake_name']
                event['description'] = event['fake_description']
                event['venue_name'] = event['fake_venue_name']

        response = {'results': events, 'count': str(count), 'pages': pages}
        return response

    @demo_mode(['address_1', 'address_2', 'city',
                'country', 'region', 'postal_code'])
    def get_event(self, event_id, fake=False):
        """ Returns an event from the database """
        event = self.database.get_item('event_aggregates', event_id)
        if event:
            if fake:
                event['name'] = event['fake_name']
                event['venue_name'] = event['fake_venue_name']
                event['description'] = event['fake_description']
                event['address_1'] = '123 Fake Street'
            # Peform type conversions on the columns
            col_to_string = ['duration', 'start_datetime', 'end_datetime']
            for column in event.keys():
                if type(event[column]) == int:
                    col_to_string.append(column)
                elif isinstance(event[column], np.int64):
                    col_to_string.append(column)
                elif event[column] in [True, False]:
                    col_to_string.append(column)
                if column in col_to_string:
                    event[column] = str(event[column])

            # Add attendees and event aggregate information
            event['attendees'] = self.get_attendees(event_id, fake=fake)
            event = self.compute_aggregates(event)

        return event

    def compute_aggregates(self, event):
        """ Computes event aggregates for the event quick facts view """
        # Compute the aggregate statistics
        start_date = str(event['start_datetime'])[:10]
        total_age = 0
        age_count = 0
        members = 0
        first_event_count = 0
        age_groups = {}
        for attendee in event['attendees']:
            # Compile age group information
            age_group_found = False
            if attendee['age']:
                # Updates for the average age
                total_age += attendee['age']
                age_count += 1

                # Update the age group count
                for group in conf.AGE_GROUPS:
                    meets_reqs = True
                    conditions = conf.AGE_GROUPS[group]
                    if 'min' in conditions:
                        if attendee['age'] < conditions['min']:
                            meets_reqs = False
                    if 'max' in conditions:
                        if attendee['age'] >= conditions['max']:
                            meets_reqs = False
                    if meets_reqs:
                        age_group_found = True
                        if group not in age_groups:
                            age_groups[group] = 1
                        else:
                            age_groups[group] += 1

            # Add to the unknown category, if necessary
            if not age_group_found:
                if 'Unknown' not in age_groups:
                    age_groups['Unknown'] = 1
                else:
                    age_groups['Unknown'] += 1

            # See if the participant is a member
            if attendee['is_member']:
                members += 1

            # Check to see if the participant is a first
            # time participants
            if not attendee['first_event_date']:
                first_event_count += 1
            else:
                first_event_date = str(attendee['first_event_date'])[:10]
                if first_event_date == start_date:
                    first_event_count += 1

        # Add age/age group information to the event
        if total_age > 0:
            average_age = total_age/age_count
        else:
            average_age = False
        event['average_age'] = average_age
        event['age_groups'] = age_groups

        # Add member breakdown to the event
        event['member_count'] = members
        event['non_member_count'] = len(event['attendees']) - members

        # Add the number of first timers
        event['first_event_count'] = first_event_count

        return event

    def get_attendees(self, event_id, fake=False):
        """ Pulls the list of the attendees for the event """
        if isinstance(event_id, int):
            event_id = str(event_id)

        prefix = 'fake_' if fake else ''
        sql = """
            SELECT DISTINCT
                a.participant_id,
                d.{prefix}first_name as first_name,
                d.{prefix}last_name as last_name,
                DATE_PART('year', AGE(now(), d.birth_date)) as age,
                CASE
                    WHEN e.active_member IS NULL THEN FALSE
                    ELSE e.active_member
                end as is_member,
                a.first_event_date,
                a.events_attended
            FROM {schema}.participants a
            INNER JOIN {schema}.attendee_to_participant b
            ON a.participant_id = b.participant_id
            INNER JOIN {schema}.attendees c
            ON b.id = c.id
            INNER JOIN {schema}.participant_match d
            ON d.id = a.participant_id
            LEFT JOIN {schema}.members_view e
            ON e.id = d.member_id
            WHERE c.event_id = %(event_id)s
            ORDER BY last_name ASC
        """.format(prefix=prefix, schema=self.database.schema)
        params = {'event_id': event_id}
        df = self.database.fetch_df(sql, params)
        attendees = self.database.to_json(df)

        # Conver the first_event_date epoch time to a timestamp
        for attendee in attendees:
            if attendee['first_event_date']:
                first = attendee['first_event_date']
                first_ts = datetime.datetime.fromtimestamp(first/1000)
                attendee['first_event_date'] = first_ts.isoformat()
        return attendees

    def get_event_cities(self):
        """ Pulls a list of events organized by city """
        sql = """
            SELECT
                event.id as event_id,
                event.name as event_name,
                venue.city as city
            FROM {schema}.events event
            INNER JOIN {schema}.venues venue
            ON event.venue_id = venue.id
        """.format(schema=self.database.schema)
        df = pd.read_sql(sql, self.database.connection)

        cities = {}
        counts = {}
        total = 0
        for i in df.index:
            row = dict(df.loc[i])
            city = row['city']
            if city:
                if row['city'] not in cities:
                    cities[city] = [row]
                    counts[city] = 1
                else:
                    cities[city].append(row)
                    counts[city] += 1
                total += 1
        counts = {x: str(counts[x]) for x in counts}

        response = {
            'results': {
                'cities': cities,
                'counts': counts
            },
            'count': str(total)
        }
        return response

    def get_event_locations(self, fake=False):
        """ Pulls the latest event at each latitude/longitude """
        prefix = 'fake_' if fake else ''
        sql = """
            SELECT
                events.event_id as event_id,
                events.start_datetime,
                event_name,
                address_1,
                city,
                events.latitude,
                events.longitude
            FROM(
                SELECT
                    max(a.id) as event_id,
                    max(start_datetime)
                    latitude,
                    longitude
                FROM {schema}.events a
                INNER JOIN {schema}.venues b
                ON a.venue_id = b.id
                GROUP BY latitude, longitude
            ) max_location
            INNER JOIN (
                SELECT
                    a.id as event_id,
                    start_datetime,
                    a.{prefix}name as event_name,
                    address_1,
                    city,
                    latitude,
                    longitude
                FROM {schema}.events a
                INNER JOIN {schema}.venues b
                ON a.venue_id = b.id
            ) events
            ON max_location.event_id = events.event_id
        """.format(schema=self.database.schema, prefix=prefix)
        df = pd.read_sql(sql, self.database.connection)

        features = []
        for i in df.index:
            row = dict(df.loc[i])
            feature = build_feature(row)
            features.append(feature)
        response = {'results': features, 'count': len(features)}
        return response

    def event_group_counts(self, start, end):
        """Returns the counts for each event group in the given date range

        Parameters
        ----------
        start: str
            a start date in 'YYYY-MM-DD' format
        end: str
            an end date in 'YYYY-MM-DD' format

        Response
        --------
        counts: dict
        """
        counts = {}
        for event_group in conf.EVENT_GROUPS:
            count = self.count_events(start, end, query=event_group)
            counts[event_group] = count
        counts['All'] = self.count_events(start, end)
        return counts

    def count_events(self, start, end, query=None):
        """Counts the number of attendees meeting the search criteria
        in the given range.

        Parameters
        ----------
        start: str
            a start date in 'YYYY-MM-DD' format
        end: str
            an end date in 'YYYY-MM-DD' format
        query: str
            a search term

        Returns
        -------
        count: int
        """
        start = "'{}'".format(start)
        end = "'{}'".format(end)
        if query:
            query = ('name', query)
        count = self.database.count_rows('event_aggregates', query=query,
                                         where=[('start_datetime', {'>=': start, 
                                                                    '<': end})])
        return count


def build_feature(row):
    """ Converts a dataframe row into a geojson feature """
    # Mask the event name and address if the app is in dev mode
    if conf.DEMO_MODE:
        row['address_1'] = 'ADDRESS'
        row['city'] = 'CITY'

    coordinates = [row['longitude'], row['latitude']]
    day = str(row['start_datetime'])[:10]
    address = ''
    if row['address_1']:
        address += row['address_1'] + ', '
    if row['city']:
        address += row['city']
    description = """
        <strong>{title}</strong>
        <ul>
            <li>Date: {day}</li>
            <li>Address: {address}</li>
        </ul>
    """.format(title=row['event_name'], day=day, address=address)

    feature = {
        "type": "Feature",
        "geometry": {
            "type": "Point",
            "coordinates": coordinates
        },
        "properties": {
            "title": row['event_name'],
            "icon": 'marker',
            "description": description
        }
    }
    return feature
