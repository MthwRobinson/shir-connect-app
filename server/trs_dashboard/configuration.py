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

# Determines which mode the app will run in
mode = os.getenv('SHIR_CONNECT_MODE')
DEMO_MODE = mode == 'DEMO' or False

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

# Roles for access control
# Admin add/modify users and upload member data
ADMIN_ROLE = 'admin'
STANDARD_ROLE = 'standard'
USER_ROLES = [ADMIN_ROLE, STANDARD_ROLE]

# Groups for access control
# Each module has a group
EVENT_GROUP = 'events'
MEMBER_GROUP = 'members'
TRENDS_GROUP = 'trends'
MAP_GROUP = 'map'
ACCESS_GROUPS = [EVENT_GROUP, MEMBER_GROUP, TRENDS_GROUP, MAP_GROUP]

# Age Group Definitions
AGE_GROUPS = {
    'College': {'min': 18, 'max': 23},
    'Young Professional': {'min': 23, 'max': 35},
    '35-50': {'min': 35, 'max': 50},
    '50-60': {'min': 50, 'max': 60},
    '60-70': {'min': 60, 'max': 70},
    'Over 80': {'min': 80}
}
