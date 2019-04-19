""" Class for pulling member information from the database. """
import datetime
import logging

import daiquiri
import pandas as pd
import numpy as np

import shir_connect.configuration as conf
from shir_connect.database.database import Database
from shir_connect.database.member_loader import MemberLoader
from shir_connect.database.utils import build_age_groups

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

    def get_member(self, first_name, last_name):
        """ Pulls the information for a member """
        sql = """
            SELECT DISTINCT
                CASE
                    WHEN a.first_name IS NOT NULL then INITCAP(a.first_name)
                    ELSE INITCAP(c.first_name)
                END as first_name,
                CASE
                    WHEN a.last_name IS NOT NULL then INITCAP(a.last_name)
                    ELSE INITCAP(c.last_name)
                END as last_name,
                DATE_PART('year', AGE(now(), birth_date)) as age,
                CASE
                    WHEN c.email IS NOT NULL THEN c.email
                    ELSE a.email
                END as email,
                CASE
                    WHEN c.first_name IS NOT NULL THEN TRUE
                    ELSE FALSE
                END as is_member,
                membership_date
            FROM {schema}.members_view c
            FULL JOIN {schema}.attendees a
            ON (lower(a.first_name) = lower(c.first_name)
            AND lower(a.last_name) = lower(c.last_name))
            LEFT JOIN {schema}.events b
            ON a.event_id = b.id
            WHERE (
                (
                    lower(a.first_name) = lower('{first_name}')
                    AND lower(a.last_name) = lower('{last_name}')
                ) OR
                (
                    lower(c.first_name) = lower('{first_name}')
                    AND lower(c.last_name) = lower('{last_name}')

                )
            )
        """.format(schema=self.database.schema, first_name=first_name,
                   last_name=last_name)

        df = pd.read_sql(sql, self.database.connection)
        df = df.where((pd.notnull(df)), None)
        if len(df) > 0:
            col_to_string = ['membership_date']
            member = dict(df.loc[0])
            for column in member.keys():
                if type(member[column]) == int:
                    col_to_string.append(column)
                elif isinstance(member[column], np.int64):
                    col_to_string.append(column)
                elif member[column] in [True, False]:
                    col_to_string.append(column)
                if column in col_to_string:
                    member[column] = str(member[column])
            member['events'] = self.get_member_events(first_name, last_name)
            return member
        else:
            return None

    def get_member_events(self, first_name, last_name):
        """ Pulls information for events a member has attended """
        sql = """
            SELECT DISTINCT
                b.id as event_id,
                b.start_datetime,
                b.name,
                d.latitude,
                d.longitude
            FROM {schema}.attendees a
            LEFT JOIN {schema}.events b
            ON a.event_id = b.id
            LEFT JOIN {schema}.venues d
            ON b.venue_id = d.id
            WHERE (
                lower(a.first_name) = lower('{first_name}')
                AND lower(a.last_name) = lower('{last_name}')
            )
            ORDER BY start_datetime DESC
        """.format(schema=self.database.schema, first_name=first_name, 
                   last_name=last_name)
        df = pd.read_sql(sql, self.database.connection)
        df = df.where((pd.notnull(df)), None)
        if len(df) > 0:
            events = []
            for i in df.index:
                event = dict(df.loc[i])
                event['start_datetime'] = str(event['start_datetime'])
                events.append(event)
            return events
        else:
            return []

    def get_members(self, limit=None, page=None, order=None, sort=None,
                    q=None, where=[]):
        """Pulls a list of members from the database

        Parameters
        ----------
        limit: int
        page: int
        order: str, the column to sort on
        sort: str, 'asc' or 'desc'
        q: tuple, a query on the last name
        where: list, the where conditions for the query

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
        response = {'results': members, 'count': str(count), 'pages': pages}
        return response

    def get_demographics(self, new_members=False):
        """Pulls the current demographics for the community based on the 
        age groups in the configuration file. """
        where = " WHERE active_member = true "
        if new_members:
            year_ago = datetime.datetime.now() - datetime.timedelta(days=365)
            year_ago_str = str(year_ago)[:10]
            where += " AND membership_date >= '{}' ".format(year_ago_str)

        age_groups = build_age_groups()
        sql = """
            SELECT COUNT(*) AS total, {age_groups}
            FROM (
                SELECT first_name, 
                       last_name,
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
        return sorted(response, key=lambda k: k['total'], reverse=True)

    def get_member_locations(self, level, limit=10,
                             start=None, end=None):
        """Pulls the current location demographics for the community.
        Available levels are city, county, and region (state)."""
        conditions = _build_member_date_range(start, end)
        sql = """
            SELECT INITCAP({level}) as location, COUNT(*) AS total
            FROM {schema}.members_view
            WHERE active_member = true
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
        return sorted(response, key=lambda k: k['total'], reverse=True)
    
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
        for i in range(start, end):
            year = i+1
            date = "'{}-01-01'".format(year)
            sql = """
                SELECT COUNT(DISTINCT household_id) as total
                FROM {schema}.members_view
                WHERE active_member = true
                AND membership_date <= '{year}-01-01'
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
        type_counts = sorted(type_counts, key=lambda k: k['total'],
                             reverse=True)
        return type_counts

    ########################
    # File upload methods
    ########################

    def upload_file(self, request):
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
        return self.member_loader.load(df)

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
    """Builds a where condition that can be added to a querty
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
