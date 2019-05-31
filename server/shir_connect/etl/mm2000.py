"""Class for handling interaction with the MM2000 CRM.
Include functionality to:
    1. Upload MM2000 membership information
    2. Upload MM2000 resignation information
"""
import logging
import os

import daiquiri
import numpy as np
import pandas as pd
import yaml

from shir_connect.database.database import Database

class MM2000:
    def __init__(self, database=None):
        daiquiri.setup(level=logging.INFO)
        self.logger = daiquiri.getLogger(__name__)

        # Load column mapping configs
        self.path = os.path.dirname(os.path.realpath(__file__))
        filename = self.path + '/member_columns.yml'
        with open(filename, 'r') as f:
            self.column_mapping = yaml.safe_load(f)
        self.database = Database() if not database else database

    #####################################
    # Methods for loading MM2000 members
    #####################################
    
    def load(self, df):
        """ Loads the data in to the member database """
        self.logger.info('Parsing MM2000 data.')
        items = self.parse_mm2000(df)

        self.logger.info('Backing up current member table.')
        self.database.backup_table('members')
        self.logger.info('Truncating current member table.')
        self.database.truncate_table('members')
        self.logger.info('Loading updated member data.')
        for item in items:
            self.database.load_item(item, 'members')

        self.logger.info('Checking updated columns.')
        good_columns = self.check_columns()
        if good_columns:
            self.logger.info('Refreshing materialized views.')
            self.database.refresh_view('members_view')
            self.database.refresh_view('participants')
            self.database.refresh_view('shape_colors')
        else:
            self.logger.warning('Column mismatch in upload')
            self.database.revert_table('members')
            return False

        return True

    def parse_mm2000(self, df):
        """ Converts the MM2000 export into a list of rows """
        column_mapping = self.column_mapping['MM2000']
        items = []
        for group in column_mapping:
            column_map = column_mapping[group]['columns']
            df_group = _group_mm2000(df, column_map)
            
            if 'id_extension' in column_mapping[group]:
                id_extension = column_mapping[group]['id_extension']
            else:
                id_extension = None

            for i in df_group.index:
                item = dict(df_group.loc[i])
                item = _parse_postal_code(item)
                item = _check_mm2000_active(item)

                # ID extension for children and spouses
                # since a family shares the same id
                item['household_id'] = item['id']
                if id_extension:
                    item['id'] += id_extension

                # Remove invalid birthdates
                item = _parse_mm2000_date(item, 'birth_date')
                item = _parse_mm2000_date(item, 'membership_date')

                # Children only have a full name, not separate
                # first names and last name
                if 'first_name' not in item and item['full_name']:
                    item['first_name'] = item['full_name'].split()[0]
                if 'last_name' not in item and item['full_name']:
                    item['last_name'] = item['full_name'].split()[0]
                if not item['first_name'] or not item['last_name']:
                    continue
                else:
                    items.append(item)
        return items

    def check_columns(self):
        """ Checks to make sure the columns are the same in the new table """
        new_columns = self.database.get_columns('members')
        old_columns = self.database.get_columns('members_backup')
        for column in new_columns:
            if column not in old_columns:
                return False
        return True

    ###########################################
    # Methods for handling MM2000 resignations
    ###########################################

    def load_resignations(self, df):
        """Loads MM2000 resignation data into the database."""
        _validate_resignation_data(df)
        # Map the file column names to the databse column names
        df = df.rename(columns=self.column_mapping['MM2000 Resignations'])
        # Drop any rows where the resignation date is null
        df = df.dropna(axis=0, how='any', subset=['resignation_date'])
        for i in df.index:
            member = dict(df.loc[i])
            
            resignation_date = str(member['resignation_date'])[:10]
            resignation_date = "'{}'".format(resignation_date)
            # TODO: This logic is specific to TRS because that's how they
            # track people who rejoined the congregation. We may have to
            # update this if another client uses MM2000
            if 'Comment1' in member:
                if 'rejoin' in str(member['Comment1']).lower():
                    resignation_date = 'NULL'
            if 'Comment2' in member:
                if 'rejoin' in str(member['Comment2']).lower():
                    resignation_date = 'NULL'

            sql = """
                UPDATE {schema}.members
                SET resignation_date = {resignation_date}
                WHERE (household_id = '{member_id}'
                       OR id = '{member_id}')
            """.format(schema=self.database.schema,
                       resignation_date=resignation_date,
                       member_id=member['id'])
            self.database.run_query(sql)

            if resignation_date != 'NULL':
                reason = _find_resignation_reason(member['resignation_reason'])
                sql = """
                    UPDATE {schema}.members
                    SET resignation_reason = '{reason}'
                    WHERE (household_id = '{member_id}'
                        OR id = '{member_id}')
                """.format(schema=self.database.schema,
                        reason=reason,
                        member_id=member['id'])
                self.database.run_query(sql)

        self.database.refresh_views()
        

def _group_mm2000(df, column_map):
    """Creates a dataframe for the specified MM2000 group
    with the appropriate column mappings."""
    source_cols = [x for x in column_map.keys()]
    dest_cols = [column_map[x] for x in column_map]

    df_group = df[source_cols].copy()
    df_group = df_group.where((pd.notnull(df_group)), None)
    df_group.columns = dest_cols
    df_group = df_group.dropna(how='all').copy()
    df_group = df_group.reset_index().copy()

    return df_group

def _parse_mm2000_date(item, column):
    """Removes invalid birthdays and membership dates."""
    if item[column]:
        if item[column].startswith('0'):
            item[column] = None
    return item

def _parse_postal_code(item):
    """Converts the postal code in an item to 5 digits."""
    postal = str(item['postal_code'])
    if '-' in postal:
        postal = postal.split('-')[0]
    if len(postal) != 5:
        postal = None
    item['postal_code'] = postal
    return item

def _check_mm2000_active(item):
    """Checks to see if an MM2000 member is active."""
    if not item['member_type']:
        active = False
    elif 'MEM' in item['member_type']:
        active = True
    elif item['member_type'] == 'STAFF':
        active = True
    else:
        active = False
    item['active_member'] = active
    return item

def _validate_resignation_data(df):
    """Checks to make sure the format of the MM2000 resignation
    date is correct. The file needs to have a Member ID columns
    and a Resign Date column."""
    if 'Member ID' not in df.columns:
        raise ValueError('Member ID is missing from the resignation file.')
    if 'Resign Date' not in df.columns:
        raise ValueError('Resign Date is missing from the resignation file.')

def _find_resignation_reason(reason):
    """Converts the resignation reason string to a category.
    TODO: if there is another client that uses MM2000 we may need
    to refactor this"""
    reason = str(reason).lower()
    if 'moving' in reason or 'move' in reason:
        category = 'Moved'
    elif 'too far' in reason:
        category = 'Too Far'
    elif 'come' in reason or 'inactive' in reason:
        category = 'Inactive'
    elif 'deceased' in reason or 'died' in reason:
        category = 'Deceased'
    elif 'mitzvah' in reason:
        category = 'Post Bar/Bat Mitzvah'
    else:
        category = 'Other'
    return category
