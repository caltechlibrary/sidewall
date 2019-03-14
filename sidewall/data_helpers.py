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

def objattr(obj, attr, default = None):
    '''Return the value of the attribute 'attr' on 'obj'.  If 'default' is
    given, return that value if there is no 'attr' on 'obj'; if 'default' is
    not given, raise an exception instead.
    '''
    if default is not None:
        try:
            return object.__getattribute__(obj, attr)
        except:
            return default
    else:
        return object.__getattribute__(obj, attr)


def set_objattr(obj, attr, value, overwrite = True):
    # Conditions for a write:
    #  1. either we're forcing a change (via overwrite), or
    #  2. the attribute has never been set, or
    #  3. it's been set but to an empty value and now we have a non-empty value.
    if (overwrite
        or attr not in objattr(obj, '__dict__')
        or (not objattr(obj, attr) and value)):
        if __debug__: log('setting "{}" on {} to "{}"', attr, id(obj), value)
        object.__setattr__(obj, attr, value)


# The following is used in methods that pull stuff out of Dimensions results.

def matching_record(json, key, obj_id):
    if not (json and key in json):
        return {}
    # Iterate over the results, matching id's until we find ours.
    for record in json[key]:
        if 'id' in record and record['id'] == obj_id:
            if __debug__: log('found matching record for id "{}"', obj_id)
            return record
    else:
        if __debug__: log('no record found for id "{}"', obj_id)
        return {}


# The following is used all over the place to either use the cache factory
# to create or return objects, or create new objects without it.  The latter
# situation comes about if the user invokes objects directly; in that case,
# they won't be passing a dimensions object to them, so the internal methods
# cant' use the factory.

def new_object(oclass, data, dimensions, creator):
    if dimensions:
        return dimensions.factory(oclass, data, creator)
    else:
        return oclass(data, creator)


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
