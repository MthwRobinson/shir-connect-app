"""Performs fuzzy matching based on participant characteristics to
resolve event attendees against a table of participants."""
import collections
import csv
import datetime
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

    def find_best_match(first_name, last_name, nickname=None, 
                        email=None, age=None):
        """Finds the best, given the criteria that is provide.
        If there are not matches, None will be returned."""
        matches = self.get_fuzzy_matches(first_name, last_name, email)
        average_age = self._get_average_age()
        if not matches:
            return None
        else:
            for match in matches:
                if not match['birth_date'] or match['birth_date'] < 0:
                    match['birth_date'] = average_age
                match_score = compute_match_score(match, *args, **kwargs)
                match['match_score'] = match_score

    
    def _get_average_age(self):
        """Pulls the average participant age. Is used if there is an
        observation that does not have an age recorded."""
        sql = """
            SELECT AVG(age) as avg_age
            FROM(
                SELECT DATE_PART('year', AGE(now(), birth_date)) as age
                FROM {schema}.participant_match
                WHERE birth_date is not null
            ) x
        """.format(schema=self.database.schema)
        df = pd.read_sql(sql, self.database.connection)
        avg_age = None
        if len(df) > 0:
            avg_age = df.loc[0]['avg_age']
        return avg_age

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

def compute_age(epoch):
    """Converts the epoch time from Postgres to an age."""
    birth_date = datetime.datetime.fromtimestamp(epoch/1000)
    now = datetime.datetime.now()
    age = (now - birth_date).days / 365
    return age
    
def compute_match_score(match, first_name, nickname=None, email=None, age=None):
        """Computes the match score for the specified match."""
        # Compute the age similarity. If a match does not have
        # an age, then the average age of all members is used
        age_score = 1
        if age:
            match_age = compute_age(match['birth_date'])
            age_score = age_similarity(age, match_age)

        name_score = name_similarity(first_name, match['first_name'],
                                     match['nickname'])

        email_score = 1
        if email:
            email_score = string_similarity(email, match['email'])

        total_score = age_score * email_score * name_score
        return total_score
