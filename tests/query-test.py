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
#sidewall.set_debug(True)

# Log in.
dimensions.login()

(total, records) = dimensions.query('search publications in title_abstract_only for "SBML" return publications')
print('total count: {}'.format(total))

for r in records:
    if not r.doi:
        print('Missing DOI: {}'.format(r.title))

import pdb; pdb.set_trace()
