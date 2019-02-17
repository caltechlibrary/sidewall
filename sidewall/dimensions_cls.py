'''
dimensions.py: Dimensions communication code for Sidewall

Authors
-------

Michael Hucka <mhucka@caltech.edu> -- Caltech Library

Copyright
---------

Copyright (c) 2019 by the California Institute of Technology.  This code is
open-source software released under a 3-clause BSD license.  Please see the
file "LICENSE" for more information.
'''

import getpass
import json as jsonlib
import keyring
import requests
import string
import sys

if sys.platform.startswith('win'):
    import keyring.backends
    from keyring.backends.Windows import WinVaultKeyring

from .debug import log
from .exceptions import *
from .network import network_available, timed_request, net
from .singleton import Singleton


# Constants
# .............................................................................

_AUTH_URL = 'https://app.dimensions.ai/api/auth.json'
'''The authentication URL used by Dimensions.'''

_DSL_URL = 'https://app.dimensions.ai/api/dsl.json'
'''The DSL network URL used by Dimensions.'''

_KEYRING = "org.caltech.library.sidewall"
'''Prefix used to create a keyring entry for the user's credentials.'''

_MAX_RETRIES = 3
'''Number of times to retry a request when server says results are not ready.'''

_RETRY_SLEEP = 2
'''How many seconds to wait between retrying a query.'''


# Classes
# .............................................................................

class Dimensions(Singleton):

    def __init__(self):
        self._use_keyring      = True
        self._reset_keyring    = False
        self._dimensions_token = None
        self._session          = requests.Session()
        self._cache            = dict()


    def login(self, username = None, password = None,
              use_keyring = True, reset_keyring = False):
        '''Store credentials for using the Dimensions network API.
        If values for 'username' and 'password' are not provided, this will
        ask the user for them interactively.  Values will be stored in the
        '''
        if __debug__: log('user = {}, pass = {}', username, 'X' if password else '')
        self._use_keyring = use_keyring
        self._reset_keyring = reset_keyring
        if not username or not password:
            (username, password) = self._credentials(username, password)

        if not network_available():
            raise NetworkFailure('No network.')

        self._dimensions_token = None
        creds = {'username': username, 'password': password}
        (resp, error) = net('post', _AUTH_URL, session = self._session, json = creds)
        if error:
            raise error

        data = resp.json()
        if 'token' in data:
            self._dimensions_token = data['token']
        else:
            raise AuthenticationFailure('Dimensions did not return a token')


    def record_search(self, query, id, retry = 0):
        search = 'search ' + query.format(id)
        cache_key = self._cache_key(search)
        if cache_key in self._cache:
            if __debug__: log("returning cached value for '{}'", search)
            return self._cache[cache_key]

        if __debug__: log("posting query '{}'", search)
        headers = {'Authorization': "JWT " + self._dimensions_token}
        (resp, error) = net('post', _DSL_URL, session = self._session,
                            data = search, headers = headers)

        # Check for problems.
        if isinstance(error, NoContent):
            if __debug__: log('Server returned a "no content" code')
            self._cache[cache_key] = {}
            return {}
        elif error:
            raise error

        # Return the results or deal with issues.
        if resp.status_code == 202:
            # Request was received by the server but not acted upon.
            if retries < _MAX_RETRIES:
                sleep(_RETRY_SLEEP)     # Sleep a short time and try again.
                return self.record_search(query, id, retry + 1)
            else:
                raise ServiceFailure('Server returned code 202 multiple times')
        elif 200 < resp.status_code <= 400:
            # Not a code 200 or 202, not a redirect, but something's not right.
            raise QueryError('Server rejected the query')
        else:
            data = resp.json()
            if __debug__: log('response: {}', data)
            self._cache[cache_key] = data
            return data


    def query(self, query, max_results = None):
        '''Issue the DSL 'query' to Dimensions and return a list of results.
        Each item will be an object such as Researcher, Publication, etc.
        The query string must end in one of the types recognized by Sidewall.
        '''

        # fixme
        # - loop over responses looking for field value
        # - issue limit & maybe multiple calls to keep looking
        pass


    def _credentials(self, user, pswd):
        '''Return stored credentials for the given combination of host and user,
        or asks the user for new credentials if none are stored or reset is True.
        Empty user names and passwords are handled too.
        '''
        NONE = '__SIDEWALL__NONE__'
        cur_user, cur_pswd = None, None
        if self._use_keyring and not self._reset_keyring:
            # This hack stores the user name as the "password" for a fake user 'user'
            if __debug__:
                if not (user or pswd): log('Trying keyring for user credentials')
            cur_user = user or keyring.get_password(_KEYRING, 'user')
            if user or (cur_user and cur_user != NONE):
                cur_pswd = pswd or keyring.get_password(_KEYRING, user or cur_user)
            elif cur_user == NONE:
                cur_pswd = NONE
        need_save = False
        if self._reset_keyring or not cur_user:
            need_save = True
            cur_user = input('User name for Dimensions: ') or NONE
        if self._reset_keyring or not cur_pswd:
            need_save = True
            cur_pswd = self._password('Password for Dimensions: ') or NONE
        if need_save and self._use_keyring:
            if __debug__: log('saving credentials to keyring')
            keyring.set_password(_KEYRING, 'user', cur_user)
            keyring.set_password(_KEYRING, cur_user, cur_pswd)
        if __debug__:
            if cur_user and cur_pswd: log('credentials obtained')
        return (None if cur_user == NONE else cur_user,
                None if cur_pswd == NONE else cur_pswd)


    def _password(self, prompt):
        # If it's a tty, use the version that doesn't echo the password.
        if sys.stdin.isatty():
            return getpass.getpass(prompt)
        else:
            sys.stdout.write(prompt)
            sys.stdout.flush()
            return sys.stdin.readline().rstrip()


    _strip_whitespace = str.maketrans('', '', string.whitespace)

    def _cache_key(self, query):
       return query.translate(self._strip_whitespace)


# Main entry point.
# .............................................................................
# The following instantiates the class and expose the interface as "dimensions".
# Callers can do things like "dimensions.login()" and "dimensions.search()"

try:
    dimensions
except NameError:
    dimensions = Dimensions()
