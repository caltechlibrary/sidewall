#!/usr/bin/env python3
# =============================================================================
# @file    pubs-missing-dois.py
# @brief   Example use of Sidewall to print authors of the 2003 SBML publication
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
results = dimensions.query('search publications in title_only for "SBML" where year=2003 return publications')
print('got back {} publications'.format(len(results)))

for p in results:
    print('-'*70)
    print('{}'.format(p.title))
    for a in p.authors:
        print('{} {} ({})'.format(a.first_name, a.last_name, a.orcid))
