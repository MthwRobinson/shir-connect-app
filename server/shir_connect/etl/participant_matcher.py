import logging

import daiquiri
import datetime
import pandas as pd
import uuid

from shir_connect.database.database import Database
from shir_connect.database.participants import Participants
from shir_connect.analytics.entity_resolution import NameResolver

class ParticipantMatcher:
    def __init__(self, database=None):
        daiquiri.setup(level=logging.INFO)
        self.logger = daiquiri.getLogger(__name__)

        self.database = Database() if not database else database
        self.name_resolver = NameResolver(database=self.database)
        self.participants = Participants(database=self.database)
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
                if attendee['first_name'] and attendee['last_name']:
                    self._process_attendee(attendee)
            n += 1
    
    def estimate_unknown_ages(self):
        """Finds estimated ages for any participant whose age is
        unknown or who has an estimated age."""
        unknowns = self._get_unknown_ages()
        for i, unknown in enumerate(unknowns):
            if i%100 == 0:
                msg = 'Estimated age for {} participants.'.format(i)
                self.logger.info(msg)

            estimated_age = self._estimate_participant_age(unknown['id'])
            if not estimated_age:
                continue
            now = datetime.datetime.now()
            estimated_birth_date = now - datetime.timedelta(estimated_age*365)
            estimated_birth_date = "'{}'".format(str(estimated_birth_date)[:10])
            self.database.update_column(table='participant_match',
                                        item_id=unknown['id'],
                                        column='birth_date',
                                        value=estimated_birth_date)
            self.database.update_column(table='participant_match',
                                        item_id=unknown['id'],
                                        column='is_birth_date_estimated',
                                        value=True)

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
            AND first_name IS NOT NULL
            AND last_name IS NOT NULL
            ORDER BY event_id ASC
            LIMIT {limit}
        """.format(schema=self.database.schema, limit=limit)
        df = pd.read_sql(sql, self.database.connection)
        return df

    def _get_avg_event_age(self, event_id):
        """Computes the average age of the attendees of an event."""
        if not isinstance(event_id, list):
            event_id = [str(event_id)]
        else:
            event_id = [str(x) for x in event_id]

        sql = """
            SELECT PERCENTILE_CONT(0.5)
                   WITHIN GROUP 
                   (ORDER BY avg_age) as avg_age
            FROM(
                SELECT event_id,
                       PERCENTILE_CONT(0.5)
                       WITHIN GROUP
                       (ORDER BY z.age) as avg_age
                FROM {schema}.attendees x
                INNER JOIN {schema}.attendee_to_participant y
                ON x.id = y.id
                INNER JOIN {schema}.participants z
                ON y.participant_id = z.participant_id
                WHERE event_id = ANY(%(event_id)s)
                AND z.age IS NOT NULL
                GROUP BY event_id
            ) a
        """.format(schema=self.database.schema, event_id=event_id)
        df = self.database.fetch_df(sql, params={'event_id': event_id})
        avg_age = None
        if len(df) > 0:
            avg_age = df.loc[0]['avg_age']
        return avg_age

    def _estimate_participant_age(self, participant_id):
        """Estimates a participants age based on who they've
        attended events with."""
        events = self.participants.get_participant_events(participant_id)
        if len(events) == 0:
            return None
        else:
            event_id = [x['event_id'] for x in events]
        age = self._get_avg_event_age(event_id)
        return age

    def _get_unknown_ages(self):
        """Pulls all participant ids that have a null date or
        and estimated date."""
        sql = """
            SELECT id
            FROM {schema}.participant_match
            WHERE is_birth_date_estimated = TRUE
            OR birth_date IS NULL
        """.format(schema=self.database.schema)
        df = pd.read_sql(sql, self.database.connection)
        results = self.database.to_json(df)
        return results

