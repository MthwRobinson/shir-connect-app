""" Class for pulling member information from the database. """
import datetime
import logging

import daiquiri
import pandas as pd
import numpy as np

import shir_connect.configuration as conf
from shir_connect.database.database import Database
from shir_connect.database.member_loader import MemberLoader
from shir_connect.database.utils import build_age_groups, sort_results

class Members:
    """ Class that handle database operations for members """
    def __init__(self, database=None):
        daiquiri.setup(level=logging.INFO)
        self.logger = daiquiri.getLogger(__name__)

        self.database = database if database else Database()
        self.member_loader = MemberLoader(database=database)

        self.allowed_extensions = conf.ALLOWED_EXTENSIONS

    ########################
    # Data fetching methods
    ########################

    def get_demographics(self, new_members=False):
        """Pulls the current demographics for the community based on the 
        age groups in the configuration file. """
        where = " WHERE active_member = true AND resignation_date IS NULL "
        if new_members:
            year_ago = datetime.datetime.now() - datetime.timedelta(days=365)
            year_ago_str = str(year_ago)[:10]
            where += " AND membership_date >= '{}' ".format(year_ago_str)

        age_groups = build_age_groups()
        sql = """
            SELECT COUNT(*) AS total, {age_groups}
            FROM (
                SELECT id, 
                       DATE_PART('year', AGE(now(), birth_date)) as age
                FROM {schema}.members
                {where}
            ) x
            GROUP BY age_group
        """.format(age_groups=age_groups, schema=self.database.schema,
                   where=where)
        df = pd.read_sql(sql, self.database.connection)
        response = self.database.to_json(df)
        total = sum([x['total'] for x in response])
        response.append({'age_group': 'All', 'total': total})
        return sort_results(response, 'age_group')

    def get_member_locations(self, level, limit=10,
                             start=None, end=None):
        """Pulls the current location demographics for the community.
        Available levels are city, county, and region (state)."""
        conditions = _build_member_date_range(start, end)
        sql = """
            SELECT INITCAP({level}) as location, COUNT(*) AS total
            FROM {schema}.members_view
            WHERE active_member = true
            AND resignation_date IS NULL
            {conditions}
            GROUP BY {level} 
            ORDER BY total DESC
        """.format(schema=self.database.schema, level=level,
                   conditions=conditions)
        df = pd.read_sql(sql, self.database.connection)
        locations = self.database.to_json(df)
        total = sum([x['total'] for x in locations])

        # Limit the number of responses
        response = []
        accounted_for = 0
        for i, item in enumerate(locations):
            if i < limit and item['location']:
                item['location'] = _clean_location_name(item['location'])
                response.append(item)
                accounted_for += item['total']

        # Figure out how many are in the "Other" category
        other = total - accounted_for
        if other > 0:
            response.append({'location': 'Other', 'total': other})
        response.append({'location': 'All', 'total': total})
        return sort_results(response, 'location')
    
    def count_new_members(self, start, end):
        """Counts the number of new members joining in the given range.

        Parameters
        ----------
        start: str
            a start date in 'YYYY-MM-DD' format
        end: str
            an end date in 'YYYY-MM-DD' format

        Returns
        -------
        count: int
        """
        start = "'{}'".format(start)
        end = "'{}'".format(end)
        count = self.database.count_rows('members_view',
                                         where=[('membership_date', 
                                                 {'>=': start, '<': end})])
        return count

    def count_new_households(self, start, end):
        """Counts the number of new members joining in the given range.

        Parameters
        ----------
        start: str
            a start date in 'YYYY-MM-DD' format
        end: str
            an end date in 'YYYY-MM-DD' format

        Returns
        -------
        count: int
        """
        sql = """
            SELECT COUNT(DISTINCT household_id) as count
            FROM {schema}.members_view
            WHERE membership_date >= '{start}'
            AND membership_date < '{end}'
        """.format(schema=self.database.schema, start=start, end=end)
        df = pd.read_sql(sql, self.database.connection)
        count = df.loc[0]['count']
        return count

    def get_households_by_year(self, start, end):
        """Counts the number of households by year.

        Parameters
        ----------
        start: int
            the starting year
        end: int
            the ending year

        Returns
        -------
        results: dict
        """
        results = []
        for i in range(start, end+1):
            year = i+1
            sql = """
                SELECT COUNT(DISTINCT household_id) as total
                FROM {schema}.members_view
                WHERE active_member = true
                AND membership_date IS NOT NULL
                AND membership_date <= '{year}-12-31'
                AND (resignation_date > '{year}-01-01'
                     OR resignation_date IS NULL)
            """.format(schema=self.database.schema, year=year)
            df = pd.read_sql(sql, self.database.connection)
            count = df.loc[0]['total']
            results.append({'year': str(i), 'count': str(count)})
        return results

    def get_household_types(self, start=None, end=None):
        """Return a count of how many house holds have each
        membership type."""
        conditions = _build_member_date_range(start, end)
        sql = """
            SELECT member_type, 
                   COUNT(DISTINCT household_id) AS total
            FROM {schema}.members_view
            WHERE active_member = true
            AND membership_date IS NOT NULL
            AND resignation_date IS NULL
            {conditions}
            GROUP BY member_type
        """.format(schema=self.database.schema, conditions=conditions)
        df = pd.read_sql(sql, self.database.connection)
        type_counts = self.database.to_json(df)

        for count in type_counts:
            if count['member_type'] in conf.MEMBER_TYPES:
                member_type = conf.MEMBER_TYPES[count['member_type']]
                count['member_type'] = member_type

        total = sum([x['total'] for x in type_counts])
        type_counts.append({'member_type': 'All', 'total': total})
        type_counts = sort_results(type_counts, 'member_type')
        return type_counts

    ########################
    # File upload methods
    ########################

    def upload_file(self, request, file_type='members'):
        """ Reads the file and uploads it to the database """
        # Check the filetype
        file_ = request.files['file']
        filename = file_.filename
        if not self.valid_extension(filename):
            return False

        # Convert the file to a dataframe
        if filename.endswith('.csv'):
            df = pd.read_csv(file_, encoding='latin-1')
        else:
            df = pd.read_excel(file_)

        if file_type == 'members':
            good_upload = self.member_loader.load(df)
        elif file_type == 'resignations':
            good_upload = self.member_loader.load_resignations(df)
        else:
            good_upload = False
        return good_upload

    def valid_extension(self, filename):
        """ Checks to make sure the filename has a valid extension """
        for extension in self.allowed_extensions:
            if filename.endswith(extension):
                return True
        return False

    def check_columns(self):
        """ Checks to make sure the columns are the same in the new table """
        new_columns = self.database.get_columns('members')
        old_columns = self.database.get_columns('members_backup')
        for column in new_columns:
            if column not in old_columns:
                return False
        return True

def _clean_location_name(name):
    """Cleans a location name for display."""
    subs = ['City', 'County']
    for sub in subs:
        name = name.replace(sub, '')
    if name.strip().lower() == 'district of columbia':
        name = 'DC'
    return name.strip()

def _build_member_date_range(start, end):
    """Builds a where condition that can be added to a query
    to restrict the membership date range (ie for new members)

    Parameters
    ----------
    start: str, 'YYYY-MM-DD'
    end: str, 'YYYY-MM-DD'

    Returns
    -------
    conditions: str
    """
    where = []
    if start:
        where.append(" membership_date >= '{}' ".format(start))
    if end:
        where.append(" membership_date <= '{}' ".format(end))

    conditions = ""
    if where:
        date_range = " AND ".join(where)
        conditions = " AND ({}) ".format(date_range)
    return conditions
