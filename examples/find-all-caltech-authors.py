#!/usr/bin/env python3
# =============================================================================
# @file    find-all-caltech-authors.py
# @brief   Use Sidewall to print authors that have Caltech affiliations
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

# Allow this program to be executed directly from the 'examples' directory.
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
results = dimensions.query('search publications where research_orgs.id = "grid.20861.3d" return publications')

print('Found {} publications from Dimensions'.format(len(results)))

for publication in results:
    for author in publication.authors:
        for org in author.affiliations:
            if org.id == "grid.20861.3d":
                print('{} {} ({})'.format(author.first_name, author.last_name, author.id))

print('Done.')
