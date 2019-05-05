import logging

import daiquiri
import pandas as pd
import uuid

from shir_connect.database.database import Database
from shir_connect.analytics.entity_resolution import NameResolver

class ParticipantMatcher:
    def __init__(self, database=None):
        daiquiri.setup(level=logging.INFO)
        self.logger = daiquiri.getLogger(__name__)

        self.database = Database() if not database else database
        self.name_resolver = NameResolver(database=self.database)
        self.avg_event_age = {}

    def run(self, limit=1000, iters=None):
        """Adds attendees that have not been matched up to a participant
        to the look up table. If there are no matches for an attendee, a
        new participant id is created."""
        n = 0
        while True:
            missing_attendees = self._get_missing_attendees(limit=limit)
            count = len(missing_attendees)
            if (iters and n >= iters) or count == 0:
                msg = 'Participant matcher has finished processing.'
                self.logger.info(msg)
                break
            msg = 'Iteration {} | Processing {} missing attendees'
            self.logger.info(msg.format(n+1, count))

            for i in range(count):
                attendee = dict(missing_attendees.loc[i])
                self._process_attendee(attendee)
            n += 1

    def _process_attendee(self, attendee):
        """Adds a link to attendee_to_participant if the attendee has a match.
        Otherwise a new participant id is created for the attendee."""
        # Cache the average age for the event so it
        # doesn't have to pull it from the database each time
        event_id = attendee['event_id']
        if event_id not in self.avg_event_age:
            age = self._get_avg_event_age(event_id)
            self.avg_event_age[event_id] = age
        else:
            age = self.avg_event_age[event_id]

        match = self.name_resolver.find_best_match(
            first_name=attendee['first_name'],
            last_name=attendee['last_name'],
            email=attendee['email'],
            age=age
        )
        if match:
            participant_id = match['id']
        else:
            # If there is no participant match, a new participant
            # is created and added to the database
            participant_id = uuid.uuid4().hex
            participant = {'id': participant_id,
                           'first_name': attendee['first_name'],
                           'last_name': attendee['last_name'],
                           'email': attendee['email']}
            self.database.load_item(participant, 'participant_match')

        # Insert the attendee to participant match to the database
        item = {'id': attendee['id'],
                'participant_id': participant_id}
        self.database.load_item(item, 'attendee_to_participant')

    def _get_missing_attendees(self, limit=1000):
        """Pulls a list of attendees that have not yet been matched
        to a participant."""
        sql = """
            SELECT id, event_id, first_name, last_name, email
            FROM {schema}.attendees
            WHERE id NOT IN (SELECT id FROM {schema}.attendee_to_participant)
            ORDER BY event_id ASC
            LIMIT {limit}
        """.format(schema=self.database.schema, limit=limit)
        df = pd.read_sql(sql, self.database.connection)
        return df

    def _get_avg_event_age(self, event_id):
        """Computes the average age of the attendees of an event."""
        sql = """
            SELECT AVG(age) as avg_age
            FROM(
                SELECT DATE_PART('year', AGE(now(), birth_date)) as age,
                       LOWER(first_name) AS first_name,
                       LOWER(last_name) AS last_name
                FROM {schema}.members
                WHERE birth_date IS NOT NULL
            ) x
            INNER JOIN (
                SELECT LOWER(first_name) as first_name,
                       LOWER(last_name) as last_name
                FROM {schema}.attendees
                WHERE event_id = '{event_id}'
            ) y
            ON (x.first_name = y.first_name 
            AND x.last_name = y.last_name)
        """.format(schema=self.database.schema, event_id=event_id)
        df = pd.read_sql(sql, self.database.connection)
        avg_age = None
        if len(df) > 0:
            avg_age = df.loc[0]['avg_age']
        return avg_age
