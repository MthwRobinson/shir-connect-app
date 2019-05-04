"""Performs fuzzy matching based on participant characteristics to
resolve event attendees against a table of participants."""
import collections
import csv
from difflib import SequenceMatcher
import functools
import logging
import operator
import os

import daiquiri
import pandas as pd

from shir_connect.database.database import Database

class NameResolver():
    """Resolves the names of participants using participant characteristics."""
    def __init__(self, database=None):
        daiquiri.setup(level=logging.INFO)
        self.logger = daiquiri.getLogger(__name__)

        self.path = os.path.dirname(os.path.realpath(__file__))
        self.database = Database() if not database else database

        self.lookup = self._read_names_file()

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

    def get_fuzzy_matches(self, first_name, last_name, email=None, tolerance=1):
        """Returns all names from the participants table that are within edit
        distance tolerance of the first name and last name."""
        select, conditions = self._first_name_sql(first_name, tolerance)

        sql = """
            SELECT id, member_id, first_name, last_name, nickname,
                   email, birth_date, is_birth_date_estimated
            FROM(
                SELECT *, {select}
                FROM {schema}.participant_match
            ) x
            WHERE
              ( ({conditions})
              AND last_name = '{last_name}')
        """.format(select=select, conditions=conditions,
                   schema=self.database.schema,
                   first_name=first_name, last_name=last_name,
                   tol=tolerance)
        if email:
            sql += " OR email='{}' ".format(email)
        df = pd.read_sql(sql, self.database.connection)
        results = self.database.to_json(df)
        return results


    def _read_names_file(self):
        """Reads the names.csv, which contains mappings of names
        to nicknames."""
        filename = os.path.join(self.path, 'names.csv')
        lookup = collections.defaultdict(list)
        with open(filename) as f:
            reader = csv.reader(f)
            for line in reader:
                matches = set(line)
                for match in matches:
                    lookup[match].append(matches)
        return lookup

    def _lookup_name(self, name):
        """Generates a sets of equivalent nicknames."""
        name = name.lower()
        if name not in self.lookup:
            return { name }
        names = functools.reduce(operator.or_, self.lookup[name])
        names.add(name)
        return names

    def _first_name_sql(self, first_name, tolerance=1):
        """Generates the select and where statments for the name
        fuzzy match."""
        nicknames = self._lookup_name(first_name)
        first_name_selects = []
        first_name_conditions = []
        for i, name in enumerate(nicknames):
            col_name = "match_first_name_{}".format(i)
            select = " lower('{}') as {} ".format(name, col_name)
            first_name_selects.append(select)
            edit_distance = """
                (levenshtein(lower(first_name), {col}) <= {tolerance}
                 OR levenshtein(lower(nickname), {col}) <= {tolerance})
            """.format(col=col_name, tolerance=tolerance)
            first_name_conditions.append(edit_distance)
        name_select = ", ".join(first_name_selects)
        name_conditions = " OR ".join(first_name_conditions)
        return name_select, name_conditions

def string_similarity(item_1, item_2):
    """Computes string similarity by looking for the largest
    contiguous matching substrings.
    """
    return SequenceMatcher(None, item_1.lower(), item_2.lower()).ratio()

def age_similarity(age_1, age_2):
    """Converts age difference to a similarity score in [0,1]"""
    difference = abs(age_1 - age_2)
    similarity =  1 - (difference/60)
    return max(0, similarity)

def name_similarity(name_1, name_2, nickname_2=None):
    """Computes the similarity of two names."""
    name_similarity = string_similarity(name_1, name_2)
    nickname_similarity = 0
    if nickname_2:
        nickname_similarity = string_similarity(name_1, nickname_2)
    return max(name_similarity, nickname_similarity)
