'''
network.py: miscellaneous network utilities for Sidewall.

Authors
-------

Michael Hucka <mhucka@caltech.edu> -- Caltech Library

Copyright
---------

Copyright (c) 2019 by the California Institute of Technology.  This code is
open-source software released under a 3-clause BSD license.  Please see the
file "LICENSE" for more information.
'''

import datetime
import http.client
from   http.client import responses as http_responses
from   os import path
import requests
from   requests.packages.urllib3.exceptions import InsecureRequestWarning
import requests_cache
from   time import sleep
import shutil
import ssl
import urllib
from   urllib import request
from   urllib.parse import urlsplit
import urllib3
import validators
import warnings

from .debug import log

# Monkey-patch requests to cache responses transparently.
requests_cache.install_cache('sidewall_cache', backend = 'sqlite',
                             expire_after = datetime.timedelta(weeks = 1))


# Constants.
# .............................................................................

_MAX_RECURSIVE_CALLS = 5
'''How many times can certain network functions call themselves upcon
encountering a network error before they stop and give up.'''

_MAX_FAILURES = 5
'''Maximum number of network failures before we give up.'''

_MAX_RETRIES = 5
'''Maximum number of times we back off and try again.  This also affects the
maximum wait time that will be reached after repeated retries.'''


# Main functions.
# .............................................................................

def network_available():
    '''Return True if it appears we have a network connection, False if not.'''
    r = None
    try:
        r = urllib.request.urlopen("http://www.google.com")
        return True
    except Exception:
        if __debug__: log('Could not connect to https://www.google.com')
        return False
    if r:
        r.close()


def timed_request(get_or_post, url, cache = True, **kwargs):
    # Wrap requests.get() or post() with a timeout.

    # Encapsulate the requests call and its arguments so that we only write
    # the argument list once (=> more maintainable).
    def url_request():
        http_method = requests.get if get_or_post == 'get' else requests.post
        return http_method(url, timeout = 10, verify = False, **kwargs)

    failures = 0
    retries = 0
    retry = True
    error = None
    while retry and failures < _MAX_FAILURES:
        retry = False
        try:
            with warnings.catch_warnings():
                # The underlying urllib3 library used by the Python requests
                # module will issue a warning about missing SSL certificates.
                # We don't care here.  See also this for a discussion:
                # https://github.com/kennethreitz/requests/issues/2214
                warnings.simplefilter("ignore", InsecureRequestWarning)
                if cache:
                    return url_request()
                else:
                    with requests_cache.disabled():
                        return url_request()
        except Exception as ex:
            # Problem might be transient.  Don't quit right away.
            if __debug__: log('timed_request() exception: {}', str(ex))
            failures += 1
            retry = True
            # Record the first error we get, not the subsequent ones, because
            # in the case of network outages, the subsequent ones will be
            # about being unable to connect and not the original problem.
            if not error:
                error = ex
        if failures >= _MAX_FAILURES:
            # Try pause & continue, in case of transient network issues.
            if retries < _MAX_RETRIES:
                retries += 1
                if __debug__: log('Pausing because of consecutive failures')
                sleep(60 * retries)
                failures = 0
                retry = True
            else:
                # We've already paused & restarted once.
                raise error


def net(get_or_post, url, polling = False, recursing = 0, **kwargs):
    '''Gets or posts the 'url' with optional keyword arguments provided.
    Returns a tuple of (response, exception), where the first element is
    the response from the get or post http call, and the second element is
    an exception object if an exception occurred.  If no exception occurred,
    the second element will be None.  This allows the caller to inspect the
    response even in cases where exceptions are raised.

    If keyword 'polling' is True, certain statuses like 404 are ignored and
    the response is returned; otherwise, they are considered errors.
    '''
    def addurl(text):
        return (text + ' for {}').format(url)

    req = None
    try:
        if __debug__: log('HTTP {} {}', get_or_post, url)
        req = timed_request(get_or_post, url, **kwargs)
    except requests.exceptions.ConnectionError as ex:
        if recursing >= _MAX_RECURSIVE_CALLS:
            return (req, NetworkFailure(addurl('Too many connection errors')))
        arg0 = ex.args[0]
        if isinstance(arg0, urllib3.exceptions.MaxRetryError):
            if __debug__: log(str(arg0))
            original = unwrapped_urllib3_exception(arg0)
            if isinstance(original, str) and 'unreacheable' in original:
                return (req, NetworkFailure(addurl('Unable to connect to server')))
            elif network_available():
                raise NetworkFailure(addurl('Unable to resolve host'))
            else:
                raise NetworkFailure(addurl('Lost network connection with server'))
        elif (isinstance(arg0, urllib3.exceptions.ProtocolError)
              and arg0.args and isinstance(args0.args[1], ConnectionResetError)):
            if __debug__: log('net() got ConnectionResetError; will recurse')
            sleep(1)                    # Sleep a short time and try again.
            recursing += 1
            return net(get_or_post, url, polling, recursing, **kwargs)
        else:
            return (req, NetworkFailure(str(ex)))
    except requests.exceptions.ReadTimeout as ex:
        if network_available():
            return (req, ServiceFailure(addurl('Timed out reading data from server')))
        else:
            return (req, NetworkFailure(addurl('Timed out reading data over network')))
    except requests.exceptions.InvalidSchema as ex:
        return (req, NetworkFailure(addurl('Unsupported network protocol')))
    except Exception as ex:
        return (req, ex)

    # Interpret the response.
    code = req.status_code
    error = None
    if code in [404, 410] and not polling:
        error = NoContent(addurl("No content found"))
    elif code in [401, 402, 403, 407, 451, 511]:
        error = AuthenticationFailure(addurl('Access is forbidden'))
    elif code in [405, 406, 409, 411, 412, 414, 417, 428, 431, 505, 510]:
        error = InternalError(addurl('Server returned code {}'.format(code)))
    elif code in [415, 416]:
        error = ServiceFailure(addurl('Server rejected the request'))
    elif code == 429:
        error = RateLimitExceeded('Server blocking further requests due to rate limits')
    elif code == 503:
        error = ServiceFailure('Server is unavailable -- try again later')
    elif code in [500, 501, 502, 506, 507, 508]:
        error = ServiceFailure('Internal server error (HTTP code {})'.format(code))
    elif not (200 <= code < 400):
        error = NetworkFailure("Unable to resolve {}".format(url))
    return (req, error)


def unwrapped_urllib3_exception(ex):
    if hasattr(ex, 'args') and isinstance(ex.args, tuple):
        return unwrapped_urllib3_exception(ex.args[0])
    else:
        return ex
