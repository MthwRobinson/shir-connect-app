"""
DAG processing file for TRS ETL processes
Note, this file only defines the structure for the DAG. The actual code to
run tasks and process data are defined elsewhere.
"""
from datetime import datetime, timedelta
import logging

from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from airflow.operators.python_operator import PythonOperator
import daiquiri

from shir_connect.etl.sources.eventbrite import EventbriteLoader
from shir_connect.database.database import Database
from shir_connect.database.fake_news import FakeNews
from shir_connect.etl.participant_matcher import ParticipantMatcher

####################################################################
# Python functions that wrap the ETL tasks for Temple Rodef Shalom
####################################################################

daiquiri.setup(level=logging.INFO)
LOGGER = daiquiri.getLogger(__name__)

EVENTBRITE_ORG = 1358538665

def load_eventbrite_data():
    """Pulls event data from Eventbrite starting at the date of the
    most recently edited event and loads them into the events table
    in the RDS database."""
    data_loader = EventbriteLoader(eventbrite_org=EVENTBRITE_ORG,
                                   database='trs')
    data_loader.run()

def refresh_materialized_views():
    """Refreshes the materialized views for Shir Connect."""
    database = Database(database='trs')
    database.refresh_views()
    print('Materialized views have been refreshed!')

def match_participants():
    """Runs the fuzzy matching algorithm to match up attendees and members."""
    database = Database(database='trs')
    participant_matcher = ParticipantMatcher(database=database)
    participant_matcher.run()
    participant_matcher.estimate_unknown_ages()

def add_fake_names():
    """Adds fake names that can be used in demo mode."""
    database = Database(database='trs')
    fake_news = FakeNews(database=database)
    fake_news.build_fake_data()

##########################################################################
# Airflow code to define the DAG for Temple Rodef Shalom's ETL processes
#########################################################################

default_args = {
    'owner': 'fiddler-analytics',
    'depends_on_past': False,
    'start_date': datetime(2019, 7, 22),
    'email': ['matt@fiddleranalytics.com',
              'ryan@fiddleranalytics.com',
              'nathan@fiddleranalytics.com'],
    'email_on_failure': True,
    'retries': 1,
    'retry_delay': timedelta(minutes=5)
}

dag = DAG('temple-rodef-shalom',
          default_args=default_args,
          schedule_interval='0 4 * * *')

trs_eventbrite_load = PythonOperator(task_id='trs-eventbrite-load',
                                     python_callable=load_eventbrite_data,
                                     dag=dag)

trs_refresh_views = PythonOperator(task_id='trs-refresh-materialized-views',
                                   python_callable=refresh_materialized_views,
                                   dag=dag)

trs_fuzzy_match = PythonOperator(task_id='trs-fuzzy-match',
                                 python_callable=match_participants,
                                 dag=dag)

trs_add_fake_names = PythonOperator(task_id='trs-add-fake-names',
                                    python_callable=add_fake_names,
                                    dag=dag=)

# Sets the order of operations for the DAG
trs_eventbrite_load >> trs_refresh_views >> trs_fuzzy_match >> trs_add_fake_names
