"""
DAG processing file for GMU Hillel ETL processes
Note, this file only defines the structure for the DAG. The actual code to
run tasks and process data are defined elsewhere.
"""
from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from airflow.operators.email_operator import EmailOperator
from airflow.operators.python_operator import PythonOperator

from shir_connect.etl.sources.eventbrite import EventbriteLoader
from shir_connect.database.database import Database

####################################################################
# Python functions that wrap the ETL tasks for GMU Hillel
####################################################################

def load_eventbrite_data():
    """Pulls event data from Eventbrite starting at the date of the
    most recently edited event and loads them into the events table
    in the RDS database."""
    data_loader = EventbriteLoader(eventbrite_org=EVENTBRITE_ORG)
    data_loader.run()

def refresh_materialized_views():
    """Refreshes the materialized views for Shir Connect."""
    database = Database()
    database.refresh_views()
    print('Materialized views have been refreshed!')

##########################################################################
# Airflow code to define the DAG for GMU Hillel's ETL processes
#########################################################################

default_args = {
    'owner': 'fiddler-analytics',
    'depends_on_past': False,
    'start_date': datetime(2019, 7, 20),
    'email': ['info@fiddleranalytics.com'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5)
}

dag = DAG('gmu-hillel',
          default_args=default_args,
          schedule_interval='35 4 * * *')

send_email = EmailOperator(task_id='email-test',
                           to='matt@fiddleranalytics.com',
                           subject='Airflow Alert Test',
                           html_content=""" <h3>Email Test</h3> """,
                           dag=dag)

# trs_refresh_views = PythonOperator(task_id='trs-refresh-materialized-views',
#                                    python_callable=load_eventbrite_data,
#                                    dag=dag)

# Sets the order of operations for the DAG
# trs_eventbrite_load >> trs_refresh_views
