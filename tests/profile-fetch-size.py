#!/usr/bin/env python3
# =============================================================================
# @file    profile.py
# @brief   Run a 1000 item query with different fetch sizes & print times
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

for fetch in [50, 100, 200, 500]:
    print('='*77)
    print('fetch_size = {}'.format(fetch))
    for _ in range(0, 3):
        pr = cProfile.Profile()
        pr.enable()
        results = dimensions.query('search publications where research_orgs.id = "grid.20861.3d" return publications',
                                   limit_results = 1000, fetch_size = fetch)
        list(results)
        pr.disable()

        stats = pstats.Stats(pr)
        stats.sort_stats('tottime')
        stats.print_stats(1)
