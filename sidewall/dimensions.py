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

from   collections import Iterable, Iterator, namedtuple
import getpass
import json as jsonlib
import keyring
import re
import requests
import string
import sys

if sys.platform.startswith('win'):
    import keyring.backends
    from keyring.backends.Windows import WinVaultKeyring

from .data_helpers import dimensions_id, list_diff, matching_record
from .debug import log
from .exceptions import *
from .network import network_available, timed_request, net
from .organization import Organization
from .publication import Publication
from .researcher import Researcher
from .singleton import Singleton


# Type definitions
# .............................................................................

Handler = namedtuple('Handler', 'objclass elaboration')
Handler.__doc__ = '''Convenience class for storing info about return types.
  'objclass' is the object class for representing objects of this type
  'elaboration' is a fieldset elaboration to be added to queries
'''


# Constants
# .............................................................................

_AUTH_URL = 'https://app.dimensions.ai/api/auth.json'
'''The authentication URL used by Dimensions.'''

_DSL_URL = 'https://app.dimensions.ai/api/dsl.json'
'''The DSL network URL used by Dimensions.'''

_KEYRING = "org.caltech.library.sidewall"
'''Prefix used to create a keyring entry for the user's credentials.'''

_KNOWN_RESULT_TYPES = {
    'publications' : Handler(Publication, '[basics+extras+book]'),
    'research_orgs': Handler(Organization, ''),
    'researchers'  : Handler(Researcher, ''),
    }
'''Known types of results that we can handle in a query.'''

_MAX_RETRIES = 3
'''Number of times to retry a request when server says results are not ready.'''

_RETRY_SLEEP = 2
'''How many seconds to wait between retrying a query.'''

# Note: my informal testing consistently showed 100 is better than 50, 200, 500
_FETCH_SIZE = 100
'''How many results to get at a time from Dimensions.'''


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


    _strip_whitespace = str.maketrans('', '', string.whitespace)

    def record_search(self, query, id, retry = 1):
        if __debug__: log('initiating record search involving {}'.format(id))
        search = 'search ' + query.format(id)
        key = search.translate(self._strip_whitespace)
        if key in self._cache:
            if __debug__: log("returning cached value for '{}'", search)
            return self._cache[key]

        if __debug__: log("posting query '{}'", search)
        headers = {'Authorization': "JWT " + self._dimensions_token}
        (resp, error) = net('post', _DSL_URL, session = self._session,
                            data = search, headers = headers)

        # Deal with problems, retry if appropriate, or fail.
        if isinstance(error, NoContent):
            if __debug__: log('server returned a "no content" code')
            self._cache[key] = {}
            return {}
        elif resp.status_code == 202:
            # Request was received by the server but not acted upon.
            if retry <= _MAX_RETRIES:
                if __debug__: log('got code 202 -- pausing & retrying')
                sleep(_RETRY_SLEEP)     # Sleep a short time and try again.
                return self.record_search(query, id, retry + 1)
            else:
                raise ServiceFailure('Server returned code 202 multiple times')
        elif resp.status_code == 400:
            raise RequestError(self._request_error_msg(resp))
        elif error:
            raise error
        else:
            data = resp.json()
            if __debug__: log('response: {}', data)
            self._cache[key] = data
            # Due to the fact that the results may not be unique and contain a
            # single record, we end up having to search for the record matching
            # the id we're interested in. The type results from Dimensions will
            # be of the form {'_stats': ..., 'TYPE': [...]} where TYPE is the
            # kind of entity in question.
            result_keys = list_diff(list(data.keys()), ['_stats'])
            if len(result_keys) > 1:
                raise DataMismatch('Unexpected keys in Dimensions results: {}'
                                   .format(list(data.keys())))
            return matching_record(data, result_keys[0], id)


    def query(self, query_string, limit_results = None, fetch_size = _FETCH_SIZE):
        '''Issue the DSL 'query_string' to Dimensions and return an iterator
        for the results.  Each item in the results will be an object such as
        Researcher, Publication, etc.  The query string must end in one of
        the types recognized by Sidewall.
        '''

        # Begin with some sanity checks
        if not query_string.startswith('search'):
            raise RequestError('Query must begin with "search"')
        result_type = self._result_type(query_string)
        if not result_type:
            txt = 'Unsupported result type -- can only handle "{}"'
            raise RequestError(txt.format('", "'.join(_KNOWN_RESULT_TYPES) + '.'))

        # Remove result limits in the query because we need to handle that.
        if re.search(r'limit\s+[0-9]+(\s+skip\s+[0-9]+)?', query_string):
            query = re.sub(r'limit\s+[0-9]+(\s+skip\s+[0-9]+)?', '', query_string).strip()

        # Prepare the first query to get the first set of results.
        if limit_results and limit_results < fetch_size:
            fetch_size = limit_results
        expanded_query = self._expanded_query(query_string)
        first_query = expanded_query + ' limit ' + str(fetch_size)

        # Need run the first query here, to get the total_count.
        data = self._post(first_query)
        if result_type not in data:
            raise DataMismatch('Data from Dimensions does not have expected result type')
        if len(data[result_type]) == 0:
            raise DataMismatch('Data inconsistency in results from Dimensions')
        if '_stats' not in data:
            raise DataMismatch('Data from Dimensions not in expected form')
        if 'total_count' not in data['_stats']:
            raise DataMismatch('Data from Dimensions missing total count')

        total = data['_stats']['total_count']
        if total == 0:
            if __debug__: log('query produced 0 results')
            return []
        else:
            if __debug__: log('query produced {}', total)
            if limit_results:
               if __debug__: log('will use limit_results {}', limit_results)
               total = limit_results

        # Hand off results processing and query iteration to the iterator.
        return queryresults(self, query_string, expanded_query, limit_results,
                            total, data, result_type, fetch_size)


    def _post(self, query, retry = 1):
        '''Post the 'query' to the server and return the result as a dict.
        '''
        if __debug__: log("posting query to server: '{}'", query)
        headers = {'Authorization': "JWT " + self._dimensions_token}
        (resp, error) = net('post', _DSL_URL, session = self._session,
                            data = query, headers = headers)

        # Deal with problems, retry if appropriate, or fail.
        if isinstance(error, NoContent):
            if __debug__: log('server returned a "no content" code')
            return []
        elif resp.status_code == 202:
            # Request was received by the server but not acted upon.
            if retry <= _MAX_RETRIES:
                if __debug__: log('got code 202 -- pausing & retrying')
                sleep(_RETRY_SLEEP)     # Sleep a short time and try again.
                return self._post(query, retry + 1)
            else:
                raise ServiceFailure('Server returned code 202 multiple times')
        elif resp.status_code == 400:
            raise RequestError(self._request_error_msg(resp))
        elif error:
            raise error
        else:
            return resp.json()


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
                if not (user or pswd): log('trying keyring for user credentials')
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


    def _result_type(self, query):
        for typename in _KNOWN_RESULT_TYPES.keys():
            if re.search(r'return\s*' + typename, query):
                return typename
        return None


    def _expanded_query(self, query):
        for typename, data in _KNOWN_RESULT_TYPES.items():
            stmt = r'return\s*' + typename
            if re.search(stmt, query):
                return re.sub(stmt, 'return ' + typename + data.elaboration, query)
        return query


    def factory(self, cls, data, creator):
        dim_id = dimensions_id(data)
        if dim_id in self._cache:
            if __debug__: log('returning cached object for "{}"', dim_id)
            return self._cache[dim_id]
        if __debug__: log('creating new {} for Dimensions object "{}"', cls, dim_id)
        new_obj = cls(data, creator = creator, dimensions_obj = self)
        if __debug__: log('object {} has {}', id(new_obj), cls)
        if dim_id:
            self._cache[dim_id] = new_obj
        return new_obj


    def cache_stats(self):
        return {'total_items': len(self._cache)}


    def _request_error_msg(self, resp):
        text = 'Server rejected the query'
        if resp.content:
            try:
                json_payload = jsonlib.loads(resp.content.decode())
                if 'errors' in json_payload.keys():
                    json_payload = json_payload['errors']
                if 'query' in json_payload.keys():
                    json_payload = json_payload['query']
                if 'details' in json_payload.keys():
                    details = json_payload['details'][0]
                text += (' -- ' + details)
            except:
                pass
        return text


class queryresults(Iterator):
    '''Results of a Dimensions query executed by Sidewall.  Instances of this
    class behave like iterators. They also have the following additional
    properties:

     'query': the original query string issued to dimensions.query(...)
     'limit_results': the limit on number of results set in the original query
     'total_count': the number of results returned by Dimensions
    '''

    def __init__(self, dim, orig_query, expanded_query, limit_results, total,
                 initial_data, result_type, fetch_size):
        if not isinstance(dim, Dimensions):
            raise TypeError('First argument must be a Dimensions object')

        # Attributes we expose
        self.query           = orig_query
        self.total_count     = total
        self.limit_results   = limit_results

        # Internal attributes.
        self._dimensions     = dim
        self._expanded_query = expanded_query
        self._initial_data   = initial_data
        self._result_type    = result_type
        self._fetch_size     = fetch_size
        self._new            = _KNOWN_RESULT_TYPES[result_type].objclass
        self._iterator       = self._results_iterator()


    def _results_iterator(self):
        skip = 0
        data = self._initial_data
        while skip < self.total_count:
            for record in data[self._result_type]:
                obj_id = record['id']
                if obj_id in self._dimensions._cache:
                    if __debug__: log('returning cached copy of {}', obj_id)
                    yield self._dimensions._cache[obj_id]
                else:
                    if __debug__: log('caching {}', obj_id)
                    new_object = self._new(record, creator = self._dimensions)
                    self._dimensions._cache[obj_id] = new_object
                    yield new_object
            skip += self._fetch_size
            query = (self._expanded_query + ' limit ' + str(self._fetch_size)
                     + ' skip ' + str(skip))
            data = self._dimensions._post(query)
        raise StopIteration


    def __len__(self):
        return self.total_count


    def __iter__(self):
        return self


    def __next__(self):
        return next(self._iterator)


# Main entry point.
# .............................................................................
# The following instantiates the class & exposes the interface as "dimensions".
# Callers can do things like "dimensions.login()" and "dimensions.search()"

try:
    dimensions
except NameError:
    dimensions = Dimensions()
