#!/usr/bin/env python3

import json as jsonlib
import os
import sys

# Allow this program to be executed directly from the 'tests' directory.
try:
    thisdir = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, os.path.join(thisdir, '..'))
except:
    sys.path.insert(0, '..')

import sidewall
from sidewall import dimensions, Publication
sidewall.set_debug(True)

# Log in so that the Researcher object can fill in fields when needed.
dimensions.login()

with open('test-data/example-two-publications.json', 'r') as f:
    data = jsonlib.load(f)
publications = []
for item in data['publications']:
    publications.append(Publication(item))

for pub in publications:
    print('id {} title {}'.format(pub.id, pub.title))
