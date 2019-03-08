'''
data_helpers: data manipulation utilities
'''

from .debug import log


# Dimensions-specific functions
# .............................................................................

def dimensions_id(data):
    return data.get('id') or data.get('researcher_id') or ''


# General-purpose functions
# .............................................................................

# The next pair of functions are to help make code more readable.  They're
# used in code called from core.__getattr__ and core.__getattribute__ because
# in those cases if you simply involke "self.x" you get infinite recursion.

def objattr(obj, attr):
    return object.__getattribute__(obj, attr)

def set_objattr(obj, attr, value, overwrite = True):
    if overwrite or attr not in objattr(obj, '__dict__') or not objattr(obj, attr):
        if __debug__: log('setting "{}" on {} to "{}"', attr, id(obj), value)
        object.__setattr__(obj, attr, value)


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


# The following choice of implementation is based on a comparison of methods
# posted by user "Moreno" to https://stackoverflow.com/a/23062482/743730

def list_diff(a, b):
  b = set(b)
  return [x for x in a if x not in b]
