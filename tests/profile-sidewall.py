#!/usr/bin/env python3
# =============================================================================
# @file    profile.py
# @brief   Profile Sidewall function calls
# @author  Michael Hucka <mhucka@caltech.edu>
# @license Please see the file named LICENSE in the project directory
# @website https://github.com/caltechlibrary/sidewall
# =============================================================================

import cProfile
import io
import os
import pstats
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

print('Sending query & building objects.')

pr = cProfile.Profile()
pr.enable()
results = dimensions.query('search publications where research_orgs.id = "grid.20861.3d" return publications',
                           limit_results = 1000)
# Creating list forces all 1000 results to be fetched and Sidewall objects built
list(results)
pr.disable()

print('Done.')
print('')
print('Reminder: "tottime" is the total time spent in the function alone.')
print('"cumtime" is the total time in the function plus all functions it calls.')
print('')

stats = pstats.Stats(pr)
stats.sort_stats('tottime')
stats.print_stats(10)
