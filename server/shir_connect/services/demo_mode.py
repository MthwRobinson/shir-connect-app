""" Decorator that scrambles the output of services so that the 
app can be shown without exposing sensitive information. """
from shir_connect.configuration import DEMO_MODE

def demo_mode(fields, demo_mode=False):
    """ If the SHIR_CONNECT_MODE environmental variable is set
    to DEMO, the decorator scrambles the output of a service
    to avoid exposing sensistive information. """
    def _scrambler(function):
        def _service(*args, **kwargs):
            response = function(*args, **kwargs)
            if DEMO_MODE or demo_mode:
                for field in fields:
                    # Fields that are passed as a string are assumed
                    # to be a string in the dictionary
                    if type(field) == str:
                        response[field] = field.upper()
                    # Fields that are passed as a dictionary are
                    # assumed to be lists
                    elif type(field) == dict:
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
