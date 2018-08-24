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
        daiquiri.setup(level=logging.INFO)
        self.logger = daiquiri.getLogger(__name__)

        self.connection = psycopg2.connect(
            user = conf.PG_USER,
            dbname = conf.PG_DATABASE,
            host = conf.PG_HOST
        )
        self.path = os.path.dirname(os.path.realpath(__file__))
