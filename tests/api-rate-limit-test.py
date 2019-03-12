#!/usr/bin/env python3
# =============================================================================
# @file    test-api-rate-limit.py
# @brief   Test the raw rate limit, without Sidewall
# @author  Michael Hucka <mhucka@caltech.edu>
# @license Please see the file named LICENSE in the project directory
# @website https://github.com/caltechlibrary/sidewall
# =============================================================================

import getpass
import os
import requests
import sys
from   time import sleep

# Global variables.
# .............................................................................

# Counter.
count = 0

# Utility functions
# .............................................................................

def post_request(url, data = None, headers = None, json = None):
    '''Call requests.post(...) with arguments, and update count.'''
    global count
    count += 1
    print('About to make post #{}'.format(count))
    if json:
        return requests.post(url, json = json)
    else:
        return requests.post(url, data = data, headers = headers)


def test():
    '''Loop until we get a code 429, pause for 90 seconds, and do it again.'''
    global count
    while True:
        resp = post_request('https://app.dimensions.ai/api/dsl.json',
                            data = 'search publications for "SBML" return publications limit 1',
                            headers = headers)
        if resp.status_code != 200:
            print('Status code {} -- pausing for 90 sec ...'.format(resp.status_code))
            sleep(90)
            print('Done sleeping -- resetting counter and resuming loop')
            count = 0


# Main code
# .............................................................................

# Get the login info from the command line.
try:
    user = input('Login name: ')
    # If it's a tty, use the version that doesn't echo the password.
    if sys.stdin.isatty():
        password = getpass.getpass('Password: ')
    else:
        sys.stdout.write('Password: ')
        sys.stdout.flush()
        password = sys.stdin.readline().rstrip()
except:
    print('Quitting')
    sys.exit(1)

login = {
    'username': user,
    'password': password,
}

# Send credentials to Dimensions and get the session token.
resp = post_request('https://app.dimensions.ai/api/auth.json', json = login)
resp.raise_for_status()

headers = {'Authorization': "JWT " + resp.json()['token']}

# Loop repeatedly until the user hits ^C.
test()
