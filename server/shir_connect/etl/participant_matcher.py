import logging

import daiquiri
import pandas as pd

from shir_connect.database.database import Database
from shir_connect.analytics.entity_resolution import NameResolver

class ParticipantMatcher:
    def __init__(self, database=None):
        daiquiri.setup(level=logging.INFO)
        self.logger = daiquiri.getLogger(__name__)

        self.database = Database() if not database else database
        self.name_resolver = NameResolver(database=self.database)
        self.avg_event_age = {}

    def _get_missing_attendees(self, limit=1000):
        """Pulls a list of attendees that have not yet been matched
        to a participant."""
        sql = """
            SELECT id, event_id
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
