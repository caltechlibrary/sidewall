'''
exceptions.py: exceptions defined by Sidewall

Authors
-------

Michael Hucka <mhucka@caltech.edu> -- Caltech Library

Copyright
---------

Copyright (c) 2019 by the California Institute of Technology.  This code is
open-source software released under a 3-clause BSD license.  Please see the
file "LICENSE" for more information.
'''

class NetworkFailure(Exception):
    '''Unrecoverable problem involving network operations.'''
    pass

class AuthenticationFailure(Exception):
    '''Problem obtaining or using authentication credentials.'''
    pass

class ServiceFailure(Exception):
    '''Unrecoverable problem involving a remote service.'''
    pass

class NoContent(Exception):
    '''Server returned a code 401 or 404, indicating no content found.'''

class RateLimitExceeded(Exception):
    '''The service flagged reports that its rate limits have been exceeded.'''
    pass

class InternalError(Exception):
    '''Unrecoverable problem involving Sidewall itself.'''
    pass

class DataMismatch(Exception):
    '''Received unexpected result from Dimensions server. This probably means
    the Dimensions API has changed recently, or it reflects a bug in Sidewall.'''
    pass

class QueryError(Exception):
    '''Problem with the query string.'''
    pass
