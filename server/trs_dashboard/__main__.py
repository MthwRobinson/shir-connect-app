""" Command line interface for server side functions """
import datetime
import logging
import os

import click
import daiquiri
from flask.cli import FlaskGroup
from gunicorn.app.wsgiapp import WSGIApplication

from trs_dashboard.database.database import Database
from trs_dashboard.etl.data_loader import DataLoader
from trs_dashboard.etl.geometries import Geometries
from trs_dashboard.services.app import app

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
def initialize():
    """ Initializes the tables for the dashboard """
    database = Database()
    LOGGER.info('Initializing the database ...')
    database.initialize()
main.add_command(initialize)

@click.command('refresh_views', help='Refreshes materialized views')
def refresh_views():
    """ Refrshes the materialized views for the dashboard """
    database = Database()
    LOGGER.info('Refreshing materialized views ...')
    database.refresh_views()
main.add_command(refresh_views)

@click.command('load_eventbrite', help='Loads data from Eventbrite')
def load_eventbrite():
    """ Loads Eventbrite data into postgres """
    start = datetime.datetime.now()
    LOGGER.info('Starting Eventbrite dataload at %s'%(start))
    data_loader = DataLoader()
    data_loader.run()
    end = datetime.datetime.now()
    LOGGER.info('Updating zip code geometries ...')
    geo = Geometries()
    zip_codes = geo.missing_zip_codes()
    for code in zip_codes:
        try:
            LOGGER.info('Loading geojson for %s'%(code))
            geo.load_zip_code(str(code))
        except:
            LOGGER.warning('Geojson load failed for %s'%(code))
    LOGGER.info('Finished Eventbrite dataload at %s'%(end))
main.add_command(load_eventbrite)

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

main()
