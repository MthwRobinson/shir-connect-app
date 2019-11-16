""" Configurations file for the REST platfrom and ETL pipeline """
import os

from shir_connect.utils import get_config

# Application paths
PATH = os.path.dirname(os.path.realpath(__file__))
PROJPATH = os.path.join(PATH, '..', '..')

# Application environmental variables
EVENTBRITE_OAUTH = os.getenv('EVENTBRITE_OAUTH')
LGL_TOKEN = os.getenv('LGL_TOKEN')
SHIR_CONNECT_ENV = os.getenv('SHIR_CONNECT_ENV')

# SMTP Configuration for E-mails
SMTP_USER = 'info@fiddleranalytics.com'
SMTP_PASSWORD = os.getenv('SMTP_PASSWORD')
SMTP_HOST = 'mail.privateemail.com'
SMTP_PORT = 587

# Secrets for API connections
JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')
JWT_ACCESS_TOKEN_EXPIRES = 30*60 # Expire access tokens after 30 mins
JWT_REFRESH_TOKEN_EXPIRES = 8*60*60 # Expire refresh tokens after 8 hours
JWT_TOKEN_LOCATION = ['cookies']
# Disable HTTPS only for local development because localhost uses HTTP
JWT_COOKIE_SECURE = SHIR_CONNECT_ENV != 'DEV'
JWT_COOKIE_CSRF_PROTECT = True

# Test configs
TEST_USER = 'unittestuser'
TEST_PASSWORD = os.getenv('UNIT_TEST_PW')

# Service configurations
ALLOWED_EXTENSIONS = ['.csv', '.xls', '.xlsx']

# Roles for access control
# Admin add/modify users and upload member data
ADMIN_ROLE = 'admin'
STANDARD_ROLE = 'standard'
USER_ROLES = [ADMIN_ROLE, STANDARD_ROLE]

# Access control groups
EVENT_GROUP = 'events'
MEMBER_GROUP = 'members'
TRENDS_GROUP = 'trends'
MAP_GROUP = 'map'
REPORT_GROUP = 'report'
ACCESS_GROUPS = [EVENT_GROUP, MEMBER_GROUP, TRENDS_GROUP,
                 MAP_GROUP, REPORT_GROUP]

# Read in the appropriate configuration file
config_file = os.getenv('SHIR_CONNECT_CONFIG')
config = get_config(PROJPATH, config_file)

# Front-end configurations
SUBDOMAIN = config['subdomain'][SHIR_CONNECT_ENV.lower()]
# Determines the default location that appears on the member
DEFAULT_LOCATION = config['location']
# Determines which moduels are available to the client
AVAILABLE_MODULES = config['modules']
# Options that determine the options that appear in the drop downs in the UI
MEMBER_TYPES = config['member_types'] if 'member_types' in config else []
EVENT_GROUPS = config['event_groups'] if 'event_groups' in config else []
MAP_EVENT_OPTIONS = config['map_event_options'] if 'map_event_options' in config else []
AGE_GROUPS = config['age_groups'] if 'age_groups' in config else []


# Database configurations and secrets
FIDDLER_RDS = os.getenv('FIDDLER_RDS')
PG_USER = 'master'
PG_HOST = FIDDLER_RDS
PG_DATABASE = config['db'][SHIR_CONNECT_ENV.lower()]
PG_SCHEMA = 'shir_connect'
MATERIALIZED_VIEWS = [
    'event_aggregates.sql',
    'members_view.sql',
    'participants.sql'
]

