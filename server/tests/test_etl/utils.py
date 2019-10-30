import re

class FakeResponse:
    def __init__(self, text, status_code):
        self.text = text
        self.status_code = status_code

def fake_request(text, status_code=200, auth_method=None, headers=None):
    """Mocks a response to a REST API. Mimics the requests library."""
    if auth_method == None:
        return FakeResponse(text, status_code)
    elif auth_method == 'header':
        authenticated = _authenticate_with_headers(headers)
        if not authenticated:
            return FakeResponse(text="""{"msg": "unauthorized"}""",
                               status_code=401)
        else:
            return FakeResponse(text, status_code)
    else:
        raise ValueError('Invalid authentication method')

def _authenticate_with_headers(headers):
    """Checks to see if the request is authenticated."""
    authenticated = False
    if isinstance(headers, dict):
        if 'Authorization' in headers:
            auth = headers['Authorization'].split()
            # Check to see if there is a token in the header
            if len(auth) == 2:
                if auth[0] == 'Bearer':
                    authenticated = True
    return authenticated

def _validate_url(url):
    """Checks to see if a url is valid. If not, raises a ValueError."""
    if not isinstance(url, str):
        raise ValueError('The url needs to be a string.')

    regex = re.compile(
            r'^(?:http|ftp)s?://' # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' #domain...
            r'localhost|' #localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
            r'(?::\d+)?' # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    valid = re.match(regex, url)
    if not valid:
        raise ValueError('The url is invalid.')
