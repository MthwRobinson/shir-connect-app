""" ETL process for loading data into Postgres """
from copy import deepcopy
import datetime
import logging
import time

import arrow
import daiquiri

import shir_connect.configuration as conf
from shir_connect.database.database import Database
from shir_connect.etl.eventbrite import Eventbrite

