""" Connects to the Postgres database """
import logging
import os

import daiquiri
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
