"""Performs fuzzy matching based on participant characteristics to
resolve event attendees against a table of participants."""
import logging

import daiquiri
import pandas as pd

from shir_connect.database.database import Database

class NameResolver():
    """Resolves the names of participants using participant characteristics."""
    def __init__(self, database=None):
        daiquiri.setup(level=logging.INFO)
        self.logger = daiquiri.getLogger(__name__)

        self.database = Database() if not database else database

    def load_member_ids(self):
        """Loads member information into the participant match table.
        Only loads names that have already been loaded into the database.
        """
        sql = """
            INSERT INTO {schema}.participant_match
            (id, member_id, first_name, last_name, nickname,
             email, birth_date, is_birth_date_estimated)
            SELECT uuid_generate_v4(), id as member_id, first_name, last_name,
                   nickname, email, birth_date, false
            FROM {schema}.members
            WHERE id NOT IN (SELECT member_id FROM {schema}.participant_match)
        """.format(schema=self.database.schema)
        self.database.run_query(sql)

    def get_fuzzy_matches(self, first_name, last_name, tolerance=2):
        """Returns all names from the participants table that are within edit
        distance tolerance of the first name and last name."""
        sql = """
            SELECT *
            FROM(
                SELECT *,
                    lower('{first_name}') as match_first_name,
                    lower('{last_name}') as match_last_name
                FROM {schema}.participant_match
            ) x
            WHERE
              (levenshtein(lower(first_name), match_first_name) <= {tol}
              OR levenshtein(lower(nickname), match_first_name) <= {tol})
              AND levenshtein(lower(last_name), match_last_name) <= {tol}
        """.format(schema=self.database.schema, first_name=first_name,
                   last_name=last_name, tol=tolerance)
        df = pd.read_sql(sql, self.database.connection)
        results = self.database.to_json(df)
        return results
