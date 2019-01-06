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

# Member upload configs
ALLOWED_EXTENSIONS = ['.csv', '.xls', '.xlsx']
COLUMN_MAPPING = {
    'time_columns': ['birth_date', 'membership_date'],
    'columns': {
        'first': 'first_name',
        'last': 'last_name',
        'zip': 'postal_code',
        'member_id': 'id',
        'memo': 'member_religion',
        'e-mail_for_member': 'email',
        'e-mail_for_spouse': 'email'
    }
}
MEMBER_COLUMNS = [
    'FIRST1',
    'LAST1',
    'NICKNAME1',
    'MEMO1',
    'ZIP1',
    'Member ID',
    'E-Mail for Member',
    'MEMBER FAMILY',
    'MEMBER TYPE',
    'MEMBERSHIP DATE',
    'BIRTH DATE1'
]
SPOUSE_COLUMNS = [
    'FIRST2',
    'LAST2',
    'NICKNAME2',
    'MEMO2',
    'ZIP2',
    'E-Mail for Spouse',
    'BIRTH DATE2'
]

