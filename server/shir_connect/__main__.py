""" Command line interface for server side functions """
import datetime
import logging
import os

import click
import daiquiri
from flask.cli import FlaskGroup
from gunicorn.app.wsgiapp import WSGIApplication

from shir_connect.analytics.entity_resolution import NameResolver
from shir_connect.database.database import Database
from shir_connect.database.fake_news import FakeNews
from shir_connect.etl.geometries import Geometries
from shir_connect.etl.participant_matcher import ParticipantMatcher
from shir_connect.services.app import app

# Configure logging
daiquiri.setup(level=logging.INFO)
LOGGER = daiquiri.getLogger(__name__)

@click.group()
def main():
    """
    Welcome to the TRS Dashboard CLI!
    To learn more about a command, use the --help flag
    """
    pass

@click.command('initialize', help='Creates the db tables')
@click.option('--drop_views', is_flag=True, help='Drops materialized views')
def initialize(drop_views=False):
    """ Initializes the tables for the dashboard """
    database = Database()
    LOGGER.info('Initializing the database ...')
    database.initialize(drop_views=drop_views)
    LOGGER.info('Loading member ids into participant match table ..')
    name_resolver = NameResolver(database=database)
    name_resolver.load_member_ids()
main.add_command(initialize)

@click.command('refresh_views', help='Refreshes materialized views')
def refresh_views():
    """Refreshes the materialized views for the dashboard """
    database = Database()
    LOGGER.info('Refreshing materialized views ...')
    database.refresh_views()
main.add_command(refresh_views)

@click.command('initialize_log_table', help='Builds the table for storing logs')
def initialize_log_table():
    """Builds the table in the postgres database that is used for storing
    application logs."""
    database = Database(database='postgres')
    LOGGER.info('Creating the application_logs schema ...')
    schema_sql = "CREATE SCHEMA IF NOT EXISTS application_logs"
    database.run_query(schema_sql)
    table_sql = """
    CREATE TABLE IF NOT EXISTS application_logs.shir_connect_logs (
        id text,
        application_user text,
        authorized boolean,
        base_url text,
        endpoint text,
        host text,
        host_url text,
        query_string text,
        referrer text,
        remote_addr text,
        scheme text,
        url text,
        url_root text,
        user_agent text,
        load_datetime timestamp
    )
    """
    LOGGER.info('Creating the shir_connect_logs table ...')
    database.run_query(table_sql)
main.add_command(initialize_log_table)

@click.command('update_geometries', help='Updates the zip code geometries')
def update_geometries():
    """Adds geometries for any missing postal codes."""
    start = datetime.datetime.now()
    LOGGER.info('Started loading geometries at %s'%(start))
    geo = Geometries()
    zip_codes = geo.missing_zip_codes()
    for code in zip_codes:
        try:
            LOGGER.info('Loading geojson for %s'%(code))
            geo.load_zip_code(str(code))
        except:
            LOGGER.warning('Geojson load failed for %s'%(code))
    LOGGER.info('Updating city, county, and state name')
    geo.load_locations()
    LOGGER.info('Refreshing views')
    geo.database.refresh_views()
    end = datetime.datetime.now()
    LOGGER.info('Finished loading geometries at %s'%(end))
main.add_command(update_geometries)

@click.command('match_participants', help='Fuzzy matches attendees to participant ids')
def match_participants():
    """ Loads Eventbrite data into postgres """
    start = datetime.datetime.now()
    LOGGER.info('Starting fuzzy matching at %s'%(start))
    participant_matcher = ParticipantMatcher()
    participant_matcher.run()
    participant_matcher.estimate_unknown_ages()
    end = datetime.datetime.now()
    LOGGER.info('Finished fuzzy matching at %s'%(end))
main.add_command(match_participants)

@click.command('launch_api', help='Runs the Flask development server')
@click.option('--prod', is_flag=True, help='Runs the WSGI prod server')
@click.option('--debug', is_flag=True, help='Runs in debug mode')
def launch_api(prod, debug):
    """ Launches the Flask app """
    if prod:
        path = os.path.dirname(os.path.realpath(__file__))
        filename = path + '/../../scripts/run_flask.sh'
        os.system('sh %s'%(filename))
    else:
        app.run(debug=debug)
main.add_command(launch_api)

@click.command('generate-fake-data')
@click.option('--sub-domain')
@click.option('--num-members')
def generate_fake_data(sub_domain, num_members):
    """Generates fake data that can be used for demos and testing

    Parameters
    ----------
    sub_domain : str
        the subdomain to generate the fake data for
    num_members : int
        the number of members to generate for the database
    """
    pass
main.add_command(generate_fake_data)

main()
