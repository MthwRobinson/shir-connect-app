""" Configurations file for the REST platfrom and ETL pipeline """
import os

# Secrets for API connections
JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')
EVENTBRITE_OAUTH = os.getenv('EVENTBRITE_OAUTH')

# Database configurations and secrets
PG_USER = 'postgres'
PG_HOST = 'localhost'
PG_DATABASE = 'postgres'
PG_SCHEMA = 'trs_dashboard'
