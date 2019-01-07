""" Configurations file for the REST platfrom and ETL pipeline """
import datetime
import os

# Paths
HOMEPATH = os.path.expanduser('~')

# Secrets for API connections
JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')
JWT_EXPIRATION_DELTA = datetime.timedelta(seconds=6000)
EVENTBRITE_OAUTH = os.getenv('EVENTBRITE_OAUTH')

# Database configurations and secrets
PG_USER = 'postgres'
PG_HOST = 'localhost'
PG_DATABASE = 'postgres'
PG_SCHEMA = 'trs_dashboard'
MATERIALIZED_VIEWS = [
    'event_aggregates.sql',
    'members_view.sql',
    'participants.sql',
    'shape_colors.sql'
]

# Service configurations
ALLOWED_EXTENSIONS = ['.csv', '.xls', '.xlsx']
USER_ROLES = ['admin', 'standard']
EVENT_GROUP = 'events'
MEMBER_GROUP = 'members'
TRENDS_GROUP = 'trends'
MAP_GROUP = 'map'
ACCESS_GROUPS = [EVENT_GROUP, MEMBER_GROUP, TRENDS_GROUP, MAP_GROUP]
