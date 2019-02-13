#!/usr/bin/env python3

import json as jsonlib
import os
import sys

# Allow this program to be executed directly from the 'tests' directory.
try:
    thisdir = os.path.dirname(os.path.abspath(__file__))
    sys.path.append(os.path.join(thisdir, '..'))
except:
    sys.path.append('..')


import sidewall
from sidewall import Researcher

with open('test-data/example-incomplete-researcher.json', 'r') as f:
    data = jsonlib.load(f)

researchers = []
for item in data['researchers']:
    researchers.append(Researcher(item))

for r in researchers:
    print('{} {}: id {}, orcid {}'.format(r.first_name, r.last_name, r.id, r.orcid))
