#!/usr/bin/env python3 -O
# =============================================================================
# @file    find-all-caltech-pubs.py
# @brief   Example use of Sidewall to print a list of all Caltech pubs
# @author  Michael Hucka <mhucka@caltech.edu>
# @license Please see the file named LICENSE in the project directory
# @website https://github.com/caltechlibrary/sidewall
# =============================================================================

# Path configuration
# .............................................................................
# The following several lines are to allow this program to be executed directly
# from the 'examples' directory without having installed Sidewall.

import os
import sys
try:
    thisdir = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, os.path.join(thisdir, '..'))
except:
    sys.path.insert(0, '..')

# Main program
# .............................................................................
# The rest of this file is the actual code for the example.

from sidewall import dimensions

print('Logging in to Dimensions')
dimensions.login()

print('Sending query to Dimensions')
pubs = dimensions.query('search publications where research_orgs.id = "grid.20861.3d" return publications')

print('Got back {} publications'.format(len(pubs)))
count = 0
for p in pubs:
    count += 1
    author = p.authors[0].last_name + (' et al.' if len(p.authors) > 1 else '')
    title  = '"' + p.title[:37] + ('...' if len(p.title) > 37 else '') + '"'
    print('[{:5}] {} - {:35} {:42} {}'.format(count, p.year, p.doi, title, author))

print('Done.')
