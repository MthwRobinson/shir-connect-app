""" Configurations file for the REST platfrom and ETL pipeline """
import datetime
import os

# Paths
HOMEPATH = os.path.expanduser('~')

# Secrets for API connections
JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')
JWT_ACCESS_TOKEN_EXPIRES = datetime.timedelta(seconds=900)
JWT_REFRESH_TOKEN_EXPIRES = datetime.timedelta(seconds=7200)
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

ADMIN_ROLE = 'admin'
STANDARD_ROLE = 'standard'
USER_ROLES = [ADMIN_ROLE, STANDARD_ROLE]

EVENT_GROUP = 'events'
MEMBER_GROUP = 'members'
TRENDS_GROUP = 'trends'
MAP_GROUP = 'map'
ACCESS_GROUPS = [EVENT_GROUP, MEMBER_GROUP, TRENDS_GROUP, MAP_GROUP]
