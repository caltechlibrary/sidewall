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

import sidewall
from sidewall import dimensions

print('Logging in to Dimensions')
dimensions.login()

# The "researcher" type is a facet of publications, and since Dimensions won't
# let you use skip syntax with facets, you can't get more than 1000 results
# using "search publications ... return researchers".  This forces us to return
# publications, then look through each pub's author list and find the authors
# that have Caltech affiliations.

print('Sending query to Dimensions')
results = dimensions.query('search publications where research_orgs.id = "grid.20861.3d" return publications')

print('Dimensions query found {} publications'.format(len(results)))
print('Finding publication authors that have Caltech affiliations')

print('-'*79)
print('{:8} {:<30} {:20} {:20}'.format('#', 'Name', 'ORCID', 'Dimensions ID'))
print('-'*79)
count = 0
for publication in results:
    for author in publication.authors:
        if "grid.20861.3d" in [org.id for org in author.affiliations]:
            count += 1
            full_name = author.last_name + ', ' + author.first_name
            print('[{:6}] {:<30} {:20} {:20}'.format(count, full_name,
                                                     author.orcid, author.id))

print('Done.')
