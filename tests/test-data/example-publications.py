#!/usr/bin/env python3

import getpass
import json
import pprint
import requests
import sys

#   The credentials to be used

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

#   Send credentials to login url to retrieve token. Raise
#   an error, if the return code indicates a problem.
#   Please use the URL of the system you'd like to access the API
#   in the example below.
resp = requests.post('https://app.dimensions.ai/api/auth.json', json=login)
resp.raise_for_status()

#   Create http header using the generated token.
headers = {
    'Authorization': "JWT " + resp.json()['token']
}

#   Execute DSL query.
resp = requests.post(
    'https://app.dimensions.ai/api/dsl.json',
    data='search publications in title_abstract_only for "SBML" return publications',
    headers=headers)

# Write to file.
with open('example-publication.json', 'w') as f:
    json.dump(resp.json(), f)
