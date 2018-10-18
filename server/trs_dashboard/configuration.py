""" Configurations file for the REST platfrom and ETL pipeline """
import datetime
import os

# Secrets for API connections
JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')
JWT_EXPIRATION_DELTA = datetime.timedelta(seconds=6000)
EVENTBRITE_OAUTH = os.getenv('EVENTBRITE_OAUTH')

# Database configurations and secrets
PG_USER = 'postgres'
PG_HOST = 'localhost'
PG_DATABASE = 'postgres'
PG_SCHEMA = 'trs_dashboard'

# Member upload confits
ALLOWED_EXTENSIONS = ['.csv', '.xls', '.xlsx']
MEMBER_COLUMNS = {
    'time_columns': ['birth_date', 'membership_date'],
    'columns': {
        'first': 'first_name',
        'last': 'last_name',
        'zip': 'postal_code',
        'member_id': 'id',
        'memo': 'member_religion',
        'e-mail_for_member': 'email'
    }
}
