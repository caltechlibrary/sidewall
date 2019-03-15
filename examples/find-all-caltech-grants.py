#!/usr/bin/env python3
# =============================================================================
# @file    find-all-caltech-grants.py
# @brief   Example use of Sidewall to print a list of all Caltech grants
# @author  Michael Hucka <mhucka@caltech.edu>
# @license Please see the file named LICENSE in the project directory
# @website https://github.com/caltechlibrary/sidewall
# =============================================================================

# Path configuration
# .............................................................................
# The following several lines are to allow this program to be executed directly
# from the 'examples' directory without having installed Sidewall.

from   humanize import intcomma
import os
import sys
try:
    thisdir = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, os.path.join(thisdir, '..'))
except:
    sys.path.insert(0, '..')

# Helper utilities
# .............................................................................

def org_info(org):
    acronym = (' (' + org.acronym + ')') if org.acronym else ''
    country = (' -- ' + org.country) if org.country else ''
    return org.name + acronym + country

# Main program
# .............................................................................
# The rest of this file is the actual code for the example.

import sidewall
from sidewall import dimensions

print('Logging in to Dimensions')
dimensions.login()

print('Sending query to Dimensions')
grants = dimensions.query('search grants where research_orgs.id = "grid.20861.3d" return grants')

print('Got back {} grants'.format(len(grants)))
for g in grants:
    print('')
    print('Title: {}'.format(g.title))
    print('Funder: {}'.format(', '.join(org_info(org) for org in g.funders)))
    print('Project number: {}'.format(g.project_num))
    print('Project year(s): {}'.format(', '.join(str(y) for y in g.active_year)))
    if g.funding_usd:
        amount = '$' + intcomma(int(g.funding_usd))
    else:
        amount = 'N/A'
    print('Funded amount: {}'.format(amount))
    print('Recipient organizations:')
    if g.research_orgs:
        for org in g.research_orgs:
            print('    {}'.format(org_info(org)))
    else:
        print('    N/A')
    print('Researchers:')
    if g.researchers:
        for r in g.researchers:
            print('    {} {}'.format(r.first_name, r.last_name))
    else:
        print('    N/A')
    print('Web link: {}'.format(g.linkout if g.linkout else 'N/A'))
    print('Dimensions ID: {}'.format(g.id))
    print('')
    print('-'*77)
