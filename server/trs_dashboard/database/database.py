""" Connects to the Postgres database """
from copy import deepcopy
import json
import logging
import os

import daiquiri
import pandas as pd
import psycopg2
from psycopg2.extras import execute_values

import trs_dashboard.configuration as conf

class Database(object):
    """ 
    Connects to the Postgres database 
    Connection settings appear in configuration.py
    Secrets must be stored in a .pgpass file
    """
    def __init__(self):
        # Configure the logger
        daiquiri.setup(level=logging.INFO)
        self.logger = daiquiri.getLogger(__name__)
        
        # Find the path to the file
        self.path = os.path.dirname(os.path.realpath(__file__))

        # Database connection and configurations
        self.materialized_views = conf.MATERIALIZED_VIEWS
        self.columns = {}
        self.schema = conf.PG_SCHEMA
        self.database = conf.PG_DATABASE
        self.connection = psycopg2.connect(
            user = conf.PG_USER,
            dbname = conf.PG_DATABASE,
            host = conf.PG_HOST
        )

    def initialize(self, drop_views=False):
        """ Initializes the database """
        self.logger.info('Initializing schema')
        self.initialize_schema()
        self.logger.info('Initializing tables')
        self.initialize_tables('sql')
        self.logger.info('Initializing views')
        self.initialize_tables('views', drop_views=drop_views)
        
    def run_query(self, sql, commit=True):
        """ Runs a query against the postgres database """
        with self.connection.cursor() as cursor:
            cursor.execute(sql)
        if commit:
            self.connection.commit()

    def initialize_schema(self):
        """ Creates the schema for the dashboard data """
        msg = 'Creating schema {schema} in database {database}'.format(
            schema=self.schema,
            database=self.database
        )
        self.logger.info(msg)
        sql = "CREATE SCHEMA IF NOT EXISTS %s"%(self.schema)
        self.run_query(sql)

    def initialize_tables(self, folder='sql', drop_views=False):
        """ Creates the tables for the dashboard data """
        path = self.path + '/%s/'%(folder)
        if folder == 'views':
            files = self.materialized_views
        else:
            files = os.listdir(path)
        for file_ in files:
            if file_.endswith('.sql'):
                table = file_.split('.')[0]
                if drop_views and folder=='views':
                    sql = """
                        DROP MATERIALIZED VIEW IF EXISTS
                        %s.%s CASCADE
                    """%(self.schema, table)
                    self.logger.info('Dropped %s'%(table))
                    self.run_query(sql)
                msg = 'Creating table or view %s in schema %s'%(
                    table,
                    self.schema
                )
                self.logger.info(msg)
                filename = path + file_
                with open(filename, 'r') as f:
                    sql = f.read().format(schema=self.schema)
                self.run_query(sql)
    
    def refresh_view(self, view):
        """ Refrshes a materialized view """
        sql = "REFRESH MATERIALIZED VIEW %s.%s"%(self.schema, view)
        self.run_query(sql)

    def refresh_views(self, test=False):
        """ Refreshes all materialized views """
        path = self.path + '/views/'
        files = os.listdir(path)
        for file_ in files:
            if file_.endswith('.sql'):
                view = file_.split('.')[0]
                msg = 'Refreshing materialized view %s'%(view)
                self.logger.info(msg)
                if not test:
                    self.refresh_view(view)

    def backup_table(self, table):
        """ Creates a backup of the specified table """
        sql = """
            DROP TABLE IF EXISTS {schema}.{table}_backup;
            CREATE TABLE {schema}.{table}_backup
            AS SELECT *
            FROM {schema}.{table}
        """.format(schema=self.schema, table=table)
        self.run_query(sql)

    def revert_table(self, table):
        """ Reverts a table to the backup """
        sql = """
            DROP TABLE IF EXISTS {schema}.{table};
            CREATE TABLE {schema}.{table}
            AS SELECT *
            FROM {schema}.{table}
        """.format(schema=self.schema, table=table)
        self.run_query(sql)

    def truncate_table(self, table):
        """ Truncates a table """
        sql = "TRUNCATE %s.%s"%(self.schema, table)
        self.run_query(sql)

    def get_columns(self, table):
        """ Pulls the column names for a table """
        sql = """
            SELECT DISTINCT column_name
            FROM information_schema.columns
            WHERE table_schema='{schema}'
            AND table_name='{table}'
        """.format(schema=self.schema, table=table)
        df = pd.read_sql(sql, self.connection)
        columns = [x for x in df['column_name']]
        return columns

    def load_item(self, item, table):
        """ Load items from a dictionary into a Postgres table """
        # Find the columns for the table
        if table not in self.columns:
            self.columns[table] = self.get_columns(table)
        columns = self.columns[table]

        # Determine which columns in the item are valid
        item_ = deepcopy(item)
        for key in item:
            if key not in columns:
                del item_[key]
        
        # Construct the insert statement
        n = len(item_)
        row = "(" + ', '.join(['%s' for i in range(n)]) + ")"
        cols = "(" + ', '.join([x for x in item_]) + ")"
        sql = """
            INSERT INTO {schema}.{table}
            {cols}
            VALUES
            {row}
        """.format(schema=self.schema, table=table, cols=cols, row=row)

        # Insert the data
        values = tuple([item_[x] for x in item_])
        with self.connection.cursor() as cursor:
            cursor.execute(sql, values)
        self.connection.commit()

    def load_items(self, items, table):
        """ 
        Loads a list of items into the database
        This is faster than running load_item in a loop
        because it reduces the number of server calls
        """
        # Find the columns for the table
        if table not in self.columns:
            self.columns[table] = self.get_columns(table)
        columns = self.columns[table]

        # Determine which columns in the item are valid
        item_ = deepcopy(items[0])
        for key in items[0]:
            if key not in columns:
                del item_[key]

        # Construct the insert statement
        n = len(item_)
        cols = "(" + ', '.join([x for x in item_]) + ")"
        sql = """
            INSERT INTO {schema}.{table}
            {cols}
            VALUES
            %s
        """.format(schema=self.schema, table=table, cols=cols)
        
        # Insert the data
        all_values = []
        for item in items:
            item_ = deepcopy(item)
            for key in item:
                if key not in columns:
                    del item_[key]
            values = tuple([item_[x] for x in item_])
            all_values.append(values)

        with self.connection.cursor() as cursor:
            execute_values(cursor, sql, all_values)
        self.connection.commit()

    def delete_item(self, table, item_id, secondary=None):
        """ Deletes an item from a table """
        sql = "DELETE FROM {schema}.{table} WHERE id='{item_id}'".format(
            schema=self.schema,
            table=table,
            item_id=item_id
        )
        if secondary:
            for key in secondary:
                sql += " AND %s='%s'"%(key, secondary[key])
        self.run_query(sql)

    def get_item(self, table, item_id, secondary=None):
        """ Fetches an item from the database """
        sql = "SELECT * FROM {schema}.{table} WHERE id='{item_id}'".format(
            schema=self.schema,
            table=table,
            item_id=item_id
        )
        df = pd.read_sql(sql, self.connection)
        if secondary:
            for key in secondary:
                sql += " AND %s='%s'"%(key, secondary[key])

        if len(df) > 0:
            return dict(df.loc[0])
        else:
            return None

    def update_column(self, table, item_id, column, value):
        """ Updates the value of the specified column """
        sql = """
            UPDATE {schema}.{table}
            SET {column} = {value}
            WHERE id = '{item_id}'
        """.format(
            schema=self.schema, 
            table=table, 
            column=column, 
            value=value,
            item_id=item_id
        )
        self.run_query(sql)

    def last_event_date(self):
        """ Pulls the most recent event start date from the database """
        sql = """
            SELECT max(start_datetime) as max_start 
            FROM {schema}.events
            WHERE start_datetime IS NOT NULL
        """.format(schema=self.schema)
        df = pd.read_sql(sql, self.connection)

        if len(df) > 0:
            time = df.loc[0]['max_start']
            if time:
                return time.to_pydatetime()
            else:
                return None

    def read_table(self, table, columns=None, sort=None, order='desc', 
        limit=None, page=None, query=None):
        """ Reads a table into a dataframe """
        if not columns:
            cols = '*'
        else:
            cols = ', '.join(columns)
        sql = """
            SELECT {cols}
            FROM {schema}.{table}
        """.format(cols=cols, schema=self.schema, table=table)
        if query:
            field = query[0]
            search_terms = query[1].split()
            conditions = []
            for term in search_terms:
                search = " lower(%s) like lower('%s%s%s') "%(
                    field, 
                    '%', term, '%'
                )
                conditions.append(search)
            sql += " WHERE " + " OR ".join(conditions)
        if sort:
            sql += " ORDER BY %s %s "%(sort, order)
        if limit:
            sql += " LIMIT %s "%(limit)
        if page and limit:
            offset = (page-1)*limit
            sql += " OFFSET %s "%(offset)
        df = pd.read_sql(sql, self.connection)
        return df
    
    def count_rows(self, table, query=None):
        """ Reads a table into a dataframe """
        sql = """
            SELECT count(*) as total
            FROM {schema}.{table}
        """.format(schema=self.schema, table=table)
        if query:
            field = query[0]
            search_terms = query[1].split()
            conditions = []
            for term in search_terms:
                search = " lower(%s) like lower('%s%s%s') "%(
                    field, 
                    '%', term, '%'
                )
                conditions.append(search)
            sql += " WHERE " + " OR ".join(conditions)
        df = pd.read_sql(sql, self.connection)
        count = df.loc[0]['total']
        return count

    def to_json(self, df):
        """ Converts a dataframe to a json list """
        return [json.loads(df.loc[i].to_json()) for i in df.index]

    def fetch_list(self, sql):
        """ Returns a sql query as a jsonfied list """
        df = pd.read_sql(sql, self.connection)
        results = self.to_json(df)
        response = {'results': results}
        return response
