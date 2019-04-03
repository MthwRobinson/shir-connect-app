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
                   sort=None, q=None, where=[]):
        """ Fetches the most recent events from the database """
        if q:
            query = ('name', q)
        else:
            query = None
        df = self.database.read_table('event_aggregates', limit=limit,
                                      page=page, order=order, sort=sort,
                                      query=query, where=where)
        count = self.database.count_rows('event_aggregates', query=query,
                                         where=where)

        pages = int((count/limit)) + 1
        events = self.database.to_json(df)
        response = {'results': events, 'count': str(count), 'pages': pages}
        return response

    @demo_mode(['address_1', 'address_2', 'city',
                'country', 'region', 'postal_code'])
    def get_event(self, event_id):
        """ Returns an event from the database """
        event = self.database.get_item('event_aggregates', event_id)
        if event:
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
            event['attendees'] = self.get_attendees(event_id)
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

    def get_attendees(self, event_id):
        """ Pulls the list of the attendees for the event """
        sql = """
            SELECT
                first_name,
                last_name,
                max(age) as age,
                CASE
                    WHEN max(is_member) = 1 THEN TRUE
                    ELSE FALSE
                end as is_member,
                max(first_event_date) as first_event_date,
                max(events_attended) as events_attended
            FROM(
                SELECT DISTINCT
                    INITCAP(a.first_name) as first_name,
                    INITCAP(a.last_name) as last_name,
                    DATE_PART('year', AGE(now(), birth_date)) as age,
                    CASE
                        WHEN c.first_name IS NOT NULL THEN 1
                        ELSE 0
                    END as is_member,
                    d.first_event_date,
                    d.events_attended
                FROM {schema}.attendees a
                INNER JOIN {schema}.events b
                on a.event_id = b.id
                LEFT JOIN {schema}.members_view c
                ON (lower(a.first_name)=lower(c.first_name)
                AND lower(a.last_name)=lower(c.last_name))
                LEFT JOIN {schema}.participants d
                ON (lower(a.first_name)=lower(d.first_name)
                AND lower(a.last_name)=lower(d.last_name))
                where b.id = '{event_id}'
            ) x
            GROUP BY first_name, last_name
            ORDER BY last_name ASC
        """.format(schema=self.database.schema, event_id=event_id)
        df = pd.read_sql(sql, self.database.connection)
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

    def get_event_locations(self):
        """ Pulls the latest event at each latitude/longitude """
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
                    a.name as event_name,
                    address_1,
                    city,
                    latitude,
                    longitude
                FROM {schema}.events a
                INNER JOIN {schema}.venues b
                ON a.venue_id = b.id
            ) events
            ON max_location.event_id = events.event_id
        """.format(schema=self.database.schema)
        df = pd.read_sql(sql, self.database.connection)

        features = []
        for i in df.index:
            row = dict(df.loc[i])
            feature = build_feature(row)
            features.append(feature)
        response = {'results': features, 'count': len(features)}
        return response

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
