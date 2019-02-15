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
from sidewall import dimensions, Journal
sidewall.set_debug(True)

j = jsonlib.loads('{"title": "Clinical Simulation in Nursing", "id": "jour.1040676"}')
journal = Journal(j)

print('id "{}" title "{}"'.format(journal.id, journal.title))
