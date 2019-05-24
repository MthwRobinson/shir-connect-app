"""Pulls participant information from the database. In Shir Connect,
a participant id resolves identities between the the event attendees
and membership tables."""
import logging

import daiquiri
import pandas as pd

import shir_connect.configuration as conf
from shir_connect.database.database import Database

class Participants:
    """Class for handling database operations for participants."""
    def __init__(self, database=None):
        daiquiri.setup(level=logging.INFO)
        self.logger = daiquiri.getLogger(__name__)

        self.database = database if database else Database()

    def get_participant(self, participant_id, fake=False):
        """Pulls information on a participant based on the participant id."""
        prefix = 'fake_' if fake else ''
        sql = """
            SELECT
                a.id as participant_id,
                a.{prefix}first_name as first_name,
                a.{prefix}last_name as last_name,
                DATE_PART('year', AGE(now(), a.birth_date)) as age,
                is_birth_date_estimated,
                a.{prefix}email as email,
                CASE
                    WHEN b.active_member IS NOT NULL THEN b.active_member
                    ELSE FALSE
                END as is_member,
                b.membership_date
            FROM (
                SELECT *
                FROM {schema}.participant_match
                WHERE id = %(participant_id)s
            ) a
            LEFT JOIN {schema}.members_view b
            ON a.member_id = b.id
        """.format(prefix=prefix, schema=self.database.schema)
        params = {'participant_id': participant_id}
        df = self.database.fetch_df(sql, params=params)
        if len(df) > 0:
            result = dict(df.loc[0])
            result['events'] = self.get_participant_events(result['participant_id'],
                                                           fake=fake)
            estimated = str(result['is_birth_date_estimated'])
            result['is_birth_date_estimated'] = estimated
            result['is_member'] = str(result['is_member'])
            result['membership_date'] = str(result['membership_date'])
            return result
        else:
            return None
    
    def get_participants(self, limit=None, page=None, order=None, sort=None,
                         q=None, where=[], fake=False):
        """Pulls a list of members from the database

        Parameters
        ----------
        limit: int
        page: int
        order: str, the column to sort on
        sort: str, 'asc' or 'desc'
        q: tuple, a query on the last name
        where: list, the where conditions for the query
        fake: bool, uses fake participant names for demo purposes if true

        Returns
        -------
        dict
        """
        query = ('last_name', q) if q else None
        df = self.database.read_table('participants', limit=limit, page=page,
                                      order=order, sort=sort, query=query, 
                                      where=where)
        count = self.database.count_rows('participants', query=query,
                                         where=where)

        pages = int((count/limit)) + 1
        members = self.database.to_json(df)

        if fake:
            for member in members:
                member['first_name'] = member['fake_first_name']
                member['last_name'] = member['fake_last_name']
                member['event_name'] = member['fake_event_name']

        response = {'results': members, 'count': str(count), 'pages': pages}
        return response

    def get_participant_events(self, participant_id, fake=False):
        """Returns a list of events that a participant has attended."""
        prefix = 'fake_' if fake else ''
        sql = """
            SELECT
                a.id as participant_id,
                d.id as event_id,
                d.{prefix}name as name,
                d.start_datetime,
                e.latitude,
                e.longitude
            FROM {schema}.participant_match a
            INNER JOIN {schema}.attendee_to_participant b
            ON a.id = b.participant_id
            INNER JOIN {schema}.attendees c
            ON c.id = b.id
            INNER JOIN {schema}.events d
            ON d.id = c.event_id
            INNER JOIN {schema}.venues e
            ON e.id = d.venue_id
            WHERE a.id = %(participant_id)s
            ORDER BY d.start_datetime DESC
        """.format(prefix=prefix, schema=self.database.schema)
        params = {'participant_id': participant_id}
        df = self.database.fetch_df(sql, params)
        
        events = []
        if len(df) > 0:
            for i in df.index:
                event = dict(df.loc[i])
                event['start_datetime'] = str(event['start_datetime'])
                events.append(event)
        return events
