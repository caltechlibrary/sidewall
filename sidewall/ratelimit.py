'''
limitcalls.py: implement rate limit handling for API calls

Object class RateLimit implements a token tracking mechanism that arranges
to return a maximum of a given number of tokens in a given amount of time.
There are to ways of using this.  The first way is simple but only suitable
when there is only one function making calls to a particular API.  Then,
the @rate_limit() decorator can be used on the function making the calls.
E.g.,

    @rate_limit(max_calls = 100, time_limit = 60)

The other way of using this system is suitable when multiple functions may
call the same API endpoint.  In that case, first create a RateLimit object
and hand that object to the @rate_limit() decorator.  E.g.:

    limits = RateLimit(30, 1)

    @rate_limit(limits)
    def first_function_calling_api():
        ... code calling the network API ...

    @rate_limit(limits)
    def second_function_calling_api():
        ... code calling the network API ...

Authors
-------

Michael Hucka <mhucka@caltech.edu> -- Caltech Library
'''

import functools
import time

from .debug import log


# Classes.
# .............................................................................

# The approach and initial code for this module came from a Stack Overflow
# posting by user "TitouanT" at https://stackoverflow.com/a/52133209/743730
# According to the terms of use of Stack Overflow, code posted there is
# licensed CC BY-SA 3.0: https://creativecommons.org/licenses/by-sa/3.0/
# This has been modified from the original.

class RateLimit:
    '''Object that distributes a maximum number of tokens every
    time_limit seconds.'''

    def __init__(self, max_calls, time_limit):
        self.max_calls = max_calls
        self.time_limit = time_limit
        self.token = max_calls
        self.time = time.perf_counter()


    def get_token(self):
        if self.token <= 0 and not self.restock():
            return False
        self.token -= 1
        return True


    def restock(self):
        now = time.perf_counter()
        if (now - self.time) < self.time_limit:
            return False
        self.token = self.max_calls
        self.time = now
        return True


# Decorator function.
# .............................................................................

def rate_limit(obj = None, *, max_calls = 30, time_limit = 1):
    '''Time_limit is in units of seconds.'''

    if obj is None:
        obj = RateLimit(max_calls, time_limit)

    def limit_decorator(func):
        @functools.wraps(func)
        def limit_wrapper(*args, **kwargs):
            if obj.get_token():
                return func(*args, **kwargs)
            return 'limit reached, please wait'
        return limit_wrapper
    return limit_decorator
