""" Configurations file for the REST platfrom and ETL pipeline """
import os

from shir_connect.utils import get_config


# Application paths
PATH = os.path.dirname(os.path.realpath(__file__))
HOMEPATH = os.path.expanduser('~')
PROJPATH = os.path.join(PATH, '..', '..')
# The subdomain is pulled from the path because on the production
# server, each instance has its own namespace
SUBDOMAIN = PATH.split('/')[-4]

# Application environmental variables 
mode = os.getenv('SHIR_CONNECT_MODE')
DEMO_MODE = mode == 'DEMO' or False
EVENTBRITE_OAUTH = os.getenv('EVENTBRITE_OAUTH')
SHIR_CONNECT_ENV = os.getenv('SHIR_CONNECT_ENV')

# Secrets for API connections
JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')
JWT_ACCESS_TOKEN_EXPIRES = 30*60 # Expire access tokens after 30 mins 
JWT_REFRESH_TOKEN_EXPIRES = 8*60*60 # Expire refresh tokens after 8 hours
JWT_TOKEN_LOCATION = ['cookies']
# Disable HTTPS only for local development because localhost uses HTTP
JWT_COOKIE_SECURE = SHIR_CONNECT_ENV != 'DEV'
JWT_COOKIE_CSRF_PROTECT = True

# Database configurations and secrets
FIDDLER_RDS = 'shir-connect.ccoaub1btbjl.us-east-1.rds.amazonaws.com'
PG_USER = 'master'
PG_HOST = 'localhost' if SHIR_CONNECT_ENV == 'DEV' else FIDDLER_RDS
PG_DATABASE = 'dev' if SHIR_CONNECT_ENV == 'DEV' else SUBDOMAIN
PG_SCHEMA = 'shir_connect'
MATERIALIZED_VIEWS = [
    'event_aggregates.sql',
    'members_view.sql',
    'participants.sql',
    'shape_colors.sql'
]

# Test configs
TEST_USER = 'unittestuser'
TEST_PASSWORD = 'YBjQOlzzzI!4jX'

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
REPORT_GROUP = 'report'
ACCESS_GROUPS = [EVENT_GROUP, MEMBER_GROUP, TRENDS_GROUP, 
                 MAP_GROUP, REPORT_GROUP]

# Custom Configurations
config = get_config(PROJPATH, HOMEPATH)
EVENT_GROUPS = config['event_groups']
AGE_GROUPS = config['age_groups']
DEFAULT_LOCATION = config['location']
IDENTIFIERS = config['identifiers']
AVAILABLE_MODULES = config['modules']
MEMBER_TYPES = config['member_types']
