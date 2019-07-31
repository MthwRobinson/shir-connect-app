""" Utilities for user for use with the Shir Connect REST services.
Most are deocrators that modify the functions that define the
REST calls. """
import re

from flask import jsonify, request
import uuid

import shir_connect.configuration as conf
from shir_connect.database.database import Database

def demo_mode(fields, demo=False):
    """ If the SHIR_CONNECT_MODE environmental variable is set
    to DEMO, the decorator scrambles the output of a service
    to avoid exposing sensistive information. """
    def _scrambler(function):
        def _service(*args, **kwargs):
            response = function(*args, **kwargs)
            if conf.DEMO_MODE or demo:
                for field in fields:
                    # Fields that are passed as a string are assumed
                    # to be a string in the dictionary
                    if isinstance(field, str):
                        response[field] = field.upper()
                    # Fields that are passed as a dictionary are
                    # assumed to be lists
                    elif isinstance(field, dict):
                        name = list(field.keys())[0]
                        keys = field[name]
                        for i, item in enumerate(response[name]):
                            for key in keys:
                                prefix = name.upper()
                                postfix = key.upper()
                                item[key] = '_'.join([prefix, postfix, str(i)])
            return response
        return _service
    return _scrambler

def validate_inputs(fields={}):
    """ Validates the arguments and query parameters for the REST
    service calls to protect against SQL injection attacks.

    Parameters
    ----------
        fields, a dictionary specifying the which fields have
            restrictions and what those restrictions are. if the
            field begins with request., it is assumed that it
            is a query parameter. available types are int and str
            example:
                fields = {
                    "event_id": {"type": "int"},
                    "request.query": {"type": "str", "min": 0, "max": 25}
                }

    Returns
    -------
       response, the json response for the service if the inputs are
            valid and a response with status code 422 if the inputs
            are not valid
    """
    def _validator(function):
        def _service(*args, **kwargs):
            results = [True]
            # Validate the request arguments. These are the same
            # in a bunch of the services so we don't make you specify
            # them in fields
            limit = request.args.get('limit')
            if limit:
                valid = validate_int(limit, 25)
                results.append(valid)
            page = request.args.get('page')
            if page:
                valid = validate_int(page)
                results.append(valid)
            order = request.args.get('order')
            if order:
                valid = order in ['asc', 'desc']
                results.append(valid)
            sort = request.args.get('sort')
            if sort:
                valid = len(sort) < 20
                results.append(valid)
            query = request.args.get('q')
            if query:
                valid = len(query) < 40
                results.append(valid)

            for field in fields:
                if field.startswith('request'):
                    param = field.split('.')[1]
                    value = request.args.get(param)
                    if not value:
                        continue
                else:
                    if field in kwargs:
                        value = kwargs[field]
                    else:
                        continue

                restrictions = fields[field]
                if 'max' in restrictions:
                    max_value = restrictions['max']
                else:
                    max_value = None
                if restrictions['type'] == 'int':
                    valid = validate_int(value, max_value)
                elif restrictions['type'] == 'str':
                    if max_value:
                        valid = len(value) < max_value
                    else:
                        valid = True
                elif restrictions['type'] == 'date':
                    valid = validate_date(value)
                results.append(valid)

            valid_call = min(results)
            if valid_call:
                response = function(*args, **kwargs)
            else:
                msg = {'message': 'bad request'}
                response = jsonify(msg), 422
            return response

        # This sets the name of _service back to the original
        # name of the function. Without this, flask will error
        # out because it will try to register two functions
        # with the same name
        _service.__name__ = function.__name__
        _service.__qualname__ = function.__qualname__
        return _service
    return _validator

def validate_int(value, max_value=None):
    """ Validates the the value can be converted to an integer
    and does not exceed the specified limit. """
    valid = True
    try:
        value = int(value)
    except ValueError:
        return False

    if max_value:
        if value > max_value:
            valid = False
    return valid

def validate_date(value):
    """ Validates that an input is a YYYY-MM-DD formatted date. """
    match = re.match(r'\d{4}-\d{2}-\d{2}', value)
    if match:
        # Checks to see if the value is the same as the match to
        # avoid accepting values like:
        # "2017-02-02;DO BAD STUFF"
        return value == value[match.start():match.end()]
    else:
        return False

def _get_cookie_from_response(response, cookie_name):
    cookie_headers = response.headers.getlist('Set-Cookie')
    for header in cookie_headers:
        attributes = header.split(';')
        if cookie_name in attributes[0]:
            cookie = {}
            for attr in attributes:
                split = attr.split('=')
                cookie[split[0].strip().lower()] = split[1] if len(split) > 1 else True
                return cookie
    return None

def check_access(user, module, database):
    """Checks to see if the user has access to the specified module. """
    user = database.get_item('users', user)
    return module in user['modules']

def log_request(request, user, authorized, database=None):
    """Logs the API request to the database for security monitoring
    and analyzing user metrics

    Parameters
    ----------
    request : request
        The flask request object for the API call
    user : str
        The user who made the API call. Pulled from the JWT.
    authorized : boolean
        Indicates whether of not the user was authorized to
        access the end point.
    database : shir_connect.database.database
        A Shir Connect database object. Primarily used for testing

    Returns
    -------
    Logs information about the request to the Postgres database.
    """
    if not database:
        database = Database(database='postgres', schema='application_logs')

    # Don't write logs to the table during unit tests or development
    if conf.SHIR_CONNECT_ENV in ['TEST']:
        return None
    else:
        item = {
            'id': uuid.uuid4().hex,
            'application_user': user,
            'authorized': authorized,
            'base_url': request.base_url,
            'endpoint': request.endpoint,
            'host': request.host,
            'host_url': request.host_url,
            'query_string': request.query_string.decode('utf-8'),
            'referrer': request.referrer,
            'remote_addr': request.remote_addr,
            'scheme': request.scheme,
            'url': request.url,
            'url_root': request.url_root,
            'user_agent': str(request.user_agent)
        }
        database.load_item(item, 'shir_connect_logs')
