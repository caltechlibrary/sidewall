#!/usr/bin/env python3
# =============================================================================
# @file    pubs-missing-dois.py
# @brief   Example use of Sidewall to print SBML pubs missing DOI
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

import sidewall
from sidewall import dimensions

# Turn on debugging mode if executed with command-line option "-d".
if len(sys.argv) > 1 and sys.argv[1] == '-d':
    sidewall.set_debug(True)

print('Logging in to Dimensions')
dimensions.login()

print('Sending query to Dimensions')
pubs = dimensions.query('search publications in title_abstract_only for "SBML" return publications')

print('Got back {} publications'.format(len(pubs)))
print('Listing publications that lack DOIs:')
for p in filter(lambda record: not record.doi, pubs):
    print('')
    author = p.authors[0].last_name + (' et al.' if len(p.authors) > 1 else '')
    title = '"' + p.title + '"'
    print('({}) {}, {}'.format(p.year, author, title))
    if p.type == 'article':
        print('{} {}({}):{}'.format(p.journal.title, p.volume, p.issue, p.pages))
    elif p.book_title:
        print('In "{}"'.format(p.book_title))
