#!/usr/bin/env python3
# =============================================================================
# @file    pubs-missing-dois.py
# @brief   Example use of Sidewall to print SBML pubs missing DOI
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

dimensions.login()

print('sending query to Dimensions')
(total, pubs) = dimensions.query('search publications in title_abstract_only for "SBML" return publications')
print('got back {} publications'.format(total))

print('SBML publications missing DOIs:')
for p in pubs:
    if not p.doi:
        print('({}) {}'.format(p.year, p.title))
