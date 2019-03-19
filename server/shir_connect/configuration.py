""" Configurations file for the REST platfrom and ETL pipeline """
import datetime
import os

import requests
import yaml


# Application paths
PATH = os.path.dirname(os.path.realpath(__file__))
HOMEPATH = os.path.expanduser('~')
PROJPATH = os.path.join(PATH, '..', '..')

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
JWT_COOKIE_SECURE = SHIR_CONNECT_ENV != 'LOCAL'
JWT_COOKIE_CSRF_PROTECT = True

# Database configurations and secrets
PG_USER = 'postgres'
PG_HOST = '13.58.50.14' if SHIR_CONNECT_ENV == 'TEST' else 'localhost'
PG_DATABASE = 'postgres'
PG_SCHEMA = 'shir_connect'
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

# Custom Configurations
custom_config = {}
ip_addr = requests.get('https://api.ipify.org').text
config_path = os.path.join(PROJPATH, 'configs')
config_files = os.listdir(config_path)
for file_ in config_files:
    filename = config_path + '/' + file_
    with open(filename, 'r') as f:
        config = yaml.safe_load(f)
    if ip_addr in config['ip_addresses']:
        custom_config = config
        break
    if config['default']:
        default_config = config
if not custom_config:
    custom_config = default_config

AGE_GROUPS = custom_config['age_groups']
