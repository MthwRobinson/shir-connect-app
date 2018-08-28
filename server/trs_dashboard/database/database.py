""" Connects to the Postgres database """
from copy import deepcopy
import logging
import os

import daiquiri
import pandas as pd
import psycopg2

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
        self.columns = {}
        self.schema = conf.PG_SCHEMA
        self.database = conf.PG_DATABASE
        self.connection = psycopg2.connect(
            user = conf.PG_USER,
            dbname = conf.PG_DATABASE,
            host = conf.PG_HOST
        )

    def initialize(self):
        """ Initializes the database """
        self.initialize_schema()
        self.initialize_tables()
        
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

    def initialize_tables(self):
        """ Creates the tables for the dashboard data """
        path = self.path + '/sql/'
        files = os.listdir(path)
        for file_ in files:
            if file_.endswith('.sql'):
                table = file_.split('.')[0]
                msg = 'Creating table {table} in schema {schema}'.format(
                    table=table,
                    schema=self.schema
                )
                self.logger.info(msg)
                filename = path + file_
                with open(filename, 'r') as f:
                    sql = f.read().format(schema=self.schema)
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

        # Inser the data
        values = tuple([item_[x] for x in item_])
        with self.connection.cursor() as cursor:
            cursor.execute(sql, values)
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

    def last_event_date(self):
        """ Pulls the most recent event start date from the database """
        sql = """
            SELECT max(start_datetime) as max_start 
            FROM {schema}.events
            WHERE start_datetime IS NOT NULL
        """.format(schema=self.schema)
        df = pd.read_sql(sql, self.connection)

        if len(df) > 0:
            return df.loc[0]['max_start'].to_pydatetime()
        else:
            return None
