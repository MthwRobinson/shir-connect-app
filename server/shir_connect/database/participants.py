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

    def get_participant(self, participant_id):
        """Pulls information on a participant based on the participant id."""
        sql = """
            SELECT
                a.id as participant_id,
                a.first_name,
                a.last_name,
                DATE_PART('year', AGE(now(), a.birth_date)) as age,
                is_birth_date_estimated,
                a.email,
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
        """.format(schema=self.database.schema)
        params = {'participant_id': participant_id}
        df = self.database.fetch_df(sql, params=params)
        if len(df) > 0:
            result = dict(df.loc[0])
            estimated = str(result['is_birth_date_estimated'])
            result['is_birth_date_estimated'] = estimated
            result['is_member'] = str(result['is_member'])
            result['membership_date'] = str(result['membership_date'])
            return result
        else:
            return None
