#!/usr/bin/env python3 -O
# =============================================================================
# @file    pubs-missing-dois.py
# @brief   Example use of Sidewall to print info about pubs by Caltech people
# @author  Michael Hucka <mhucka@caltech.edu>
# @license Please see the file named LICENSE in the project directory
# @website https://github.com/caltechlibrary/sidewall
# =============================================================================

import os
import sys

# Allow this program to be executed directly from the 'examples' directory.
try:
    thisdir = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, os.path.join(thisdir, '..'))
except:
    sys.path.insert(0, '..')

import sidewall
from sidewall import dimensions

if len(sys.argv) > 1 and sys.argv[1] == '-d':
    sidewall.set_debug(True)

dimensions.login()

print('sending query to Dimensions')
pubs = dimensions.query('search publications where research_orgs.id = "grid.20861.3d" return publications')
print('got back {} publications'.format(len(pubs)))

for p in pubs:
    print('({}) {} - {}'.format(p.year, p.doi, p.title), )
