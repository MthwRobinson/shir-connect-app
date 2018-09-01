""" Command line interface for server side functions """
import datetime
import logging

import click
import daiquiri

from trs_dashboard.database.database import Database
from trs_dashboard.etl.data_loader import DataLoader

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

@click.command()
def initialize():
    """ Initializes the tables for the dashboard """
    database = Database()
    LOGGER.info('Initializing the database ...')
    database.initialize()
main.add_command(initialize)

@click.command()
def refresh_views():
    """ Refrshes the materialized views for the dashboard """
    database = Database()
    LOGGER.info('Refreshing materialized views ...')
    database.refresh_views()
main.add_command(refresh_views)

@click.command()
def load_eventbrite():
    """ Loads Eventbrite data into postgres """
    start = datetime.datetime.now()
    LOGGER.info('Starting Eventbrite dataload at %s'%(start))
    data_loader = DataLoader()
    data_loader.run()
    end = datetime.datetime.now()
    LOGGER.info('Finished Eventbrite dataload at %s'%(end))
main.add_command(load_eventbrite)

main()
