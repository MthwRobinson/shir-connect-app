""" Utilities for user for use with the Shir Connect REST services.
Most are deocrators that modify the functions that define the
REST calls. """
from flask import jsonify, request

from shir_connect.configuration import DEMO_MODE

def demo_mode(fields, demo=False):
    """ If the SHIR_CONNECT_MODE environmental variable is set
    to DEMO, the decorator scrambles the output of a service
    to avoid exposing sensistive information. """
    def _scrambler(function):
        def _service(*args, **kwargs):
            response = function(*args, **kwargs)
            if DEMO_MODE or demo:
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
