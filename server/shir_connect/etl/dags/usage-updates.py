"""
DAG processing file for sending updates on weekly usage statistics
Note, this file only defines the structure for the DAG. The actual code to
run tasks and process data are defined elsewhere.
"""
from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.email_operator import EmailOperator
import pandas as pd

from shir_connect.database.database import Database

######################################################################
# Python functions that wrap the ETL tasks for weekly usage statistics
######################################################################

def build_email_content():
    """Builds the email with the weekly usage statistics."""
    database = Database(database='postgres', schema='application_logs')

    all_time_sql = """
        SELECT COUNT(*) as total, application_user,
               remote_addr, host, user_agent
        FROM application_logs.shir_connect_logs
        WHERE load_datetime >= NOW() - INTERVAL '7 DAYS'
        GROUP BY application_user, host, remote_addr, user_agent
        ORDER BY application_user ASC
    """
    all_time_stats = pd.read_sql(all_time_sql, database.connection)
    all_time_html = all_time_stats.to_html()

    weekly_sql = """
        SELECT COUNT(*) as total, application_user,
               remote_addr, host, user_agent
        FROM application_logs.shir_connect_logs
        WHERE load_datetime >= '2018-08-01'
        GROUP BY application_user, host, remote_addr, user_agent
        ORDER BY application_user ASC
    """
    weekly_stats = pd.read_sql(weekly_sql, database.connection)
    weekly_html = weekly_stats.to_html()

    html = """
        <h3>Usage Statistics</h3>
        <p>Greetings Fiddlers! Here are the latest usage statistics for Shir Connect.</p>
        <h4>Overall Usage</h4>
        {all_time_html}
        <h4>Weekly Usage</h4>
        {weekly_html}
    """.format(all_time_html, weekly_html)
    return html

##########################################################################
# Airflow code to define the DAG for the weekly usage updates
#########################################################################

default_args = {
    'owner': 'fiddler-analytics',
    'depends_on_past': False,
    'start_date': datetime(2019, 8, 18),
    'email': ['matt@fiddleranalytics.com',
              'nathan@fiddleranalytics.com',
              'ryan@fiddleranalytics.com'],
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5)
}

dag = DAG('shir-connect-usage',
          default_args=default_args,
          schedule_interval='0 12 * * 5')

send_email = EmailOperator(task_id='usage-statistics-email',
                           to=['matt@fiddleranalytics.com',
                               'nathan@fiddleranalytics.com',
                               'ryan@fiddleranalytics.com'],
                           subject='Shir Connect Usage Statistics',
                           html_content=build_html_content(),
                           dag=dag)
