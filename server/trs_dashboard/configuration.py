""" Configurations file for the REST platfrom and ETL pipeline """
import os

EVENTBRITE_OAUTH = os.getenv('EVENTBRITE_OAUTH')
PG_USER = 'postgres'
PG_HOST = 'localhost'
PG_DATABASE = 'postgres'
