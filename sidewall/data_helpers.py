'''
data_helpers: data manipulation utilities
'''

import json as jsonlib


# Dimensions-specific functions
# .............................................................................

def dimensions_id(data):
    return data.get('id') or data.get('researcher_id') or ''


# General-purpose functions
# .............................................................................

# The following originally came from a posting by user Zero Piraeus here:
# https://stackoverflow.com/a/25851972/743730

def ordered(obj):
    '''Recursively sorts any lists it finds.'''
    if isinstance(obj, dict):
        return sorted((k, ordered(v)) for k, v in obj.items())
    if isinstance(obj, list):
        return sorted(ordered(x) for x in obj)
    else:
        return obj
