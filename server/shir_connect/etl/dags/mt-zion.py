"""
DAG processing file for Mt Zion ETL processes
Note, this file only defines the structure for the DAG. The actual code to
run tasks and process data are defined elsewhere.
"""
from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from airflow.operators.python_operator import PythonOperator

from shir_connect.etl.sources.eventbrite import EventbriteLoader
from shir_connect.database.database import Database

####################################################################
# Python functions that wrap the ETL tasks for Mt Zion
####################################################################

def test_email_on_failure():
    """Pulls event data from Eventbrite starting at the date of the
    most recently edited event and loads them into the events table
    in the RDS database."""
    raise ValueError('Oh no! The Mt Zion ETL processes failed!')

def refresh_materialized_views():
    """Refreshes the materialized views for Shir Connect."""
    database = Database()
    database.refresh_views()
    print('Materialized views have been refreshed!')

##########################################################################
# Airflow code to define the DAG for Mt Zion's ETL processes
#########################################################################

default_args = {
    'owner': 'fiddler-analytics',
    'depends_on_past': False,
    'start_date': datetime(2019, 7, 20),
    'email': ['matt@fiddleranalytics.com',
              'ryan@fiddleranalytics.com',
              'nathan@fiddleranalytics.com'],
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5)
}

dag = DAG('mt-zion',
          default_args=default_args,
          schedule_interval='30 4 * * *')

test_email = PythonOperator(task_id='test-email-on-failure',
                            python_callable=test_email_on_failure,
                            dag=dag)

refresh_views = PythonOperator(task_id='refresh-materialized-views',
                               python_callable=refresh_materialized_views,
                               dag=dag)

# Sets the order of operations for the DAG
test_email >> refresh_views
