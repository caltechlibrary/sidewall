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
from sidewall import dimensions, Researcher
sidewall.set_debug(True)

# Log in so that the Researcher object can fill in 'orcid' value when needed.
dimensions.login()

with open('test-data/example-incomplete-researcher.json', 'r') as f:
    data = jsonlib.load(f)
researchers = []
for item in data['researchers']:
    researchers.append(Researcher(item))

for r in researchers:
    print('{} {}: id {}, orcid {}'.format(r.first_name, r.last_name, r.id, r.orcid))
