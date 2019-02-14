'''
core.py: core object classes for Sidewall.

Authors
-------

Michael Hucka <mhucka@caltech.edu> -- Caltech Library

Copyright
---------

Copyright (c) 2019 by the California Institute of Technology.  This code is
open-source software released under a 3-clause BSD license.  Please see the
file "LICENSE" for more information.
'''

import json as jsonlib

from .dimensions import dimensions_search
from .debug import log


# Classes
# .............................................................................

# if json is not None:
#     if '_stats' in json and 'total_count' in json['_stats']:
#         self._total_count = json['_stats']['total_count']
#     else:
#         raise DataMismatch('Missing value in Dimensions JSON')

class DimensionsCore(object):
    _attributes = []

    def __init__(self, json, creds = None):
        self._json_data = json          # A dict.
        self._creds = creds             # User credentials.
        self._searched = False          # If we already searched for more.
        self._hash = None
        try:
            self._update_attributes(json)
        except KeyError as err:
            raise DataMismatch('Incomplete response from Dimensions')


    def _update_attributes(self, json):
        '''Method stub for subclasses to override.'''
        pass


    def __getattr__(self, attr):
        # Be careful not to invoke "self.x" b/c it causes infinite recursion.
        # Make every attribute lookup use object.__getattribute__.
        objattr = object.__getattribute__
        if attr in objattr(self, '_attributes'):
            existing_attrs = objattr(self, '__dict__')
            if attr not in existing_attrs:
                if __debug__: log('setting "{}" on object {}', attr, id(self))
                json = objattr(self, '_json_data')
                if attr in json:
                    value = self._json_data.get(attr)
                    object.__setattr__(self, attr, value)
                    return value
        return objattr(self, attr)


    def __getattribute__(self, attr):
        # Be careful not to invoke "self.x" b/c it causes infinite recursion.
        # Make every attribute lookup use object.__getattribute__.
        if __debug__: log('looking up "{}" on object {}', attr, id(self))
        objattr = object.__getattribute__
        if not attr in objattr(self, '_attributes'):
            raise AttributeError(attr)
        if not (objattr(self, attr) or objattr(self, '_searched')):
            if __debug__: log('"{}" not yet set', attr)
            creds = objattr(self, '_creds')
            search_tmpl = objattr(self, '_search_tmpl')
            if creds and search_tmpl:
                object.__setattr__(self, '_searched', True)
                dim_id = objattr(self, 'id')
                record_json = dimensions_search(search_tmpl, dim_id, creds)
                fill_record = objattr(self, '_fill_record')
                fill_record(record_json)
        return objattr(self, attr)


    def __repr__(self):
        return "<DimensionsCore 0x{0:x}>".format(id(self))


    def __eq__(self, other):
        return (isinstance(other, self.__class__)
                and ordered(self) == ordered(other))


    def __ne__(self, other):
        return not self.__eq__(other)


    def __gt__(self, other):
        return not __le__(self, other)


    def __ge__(self, other):
        return not __lt__(self, other)


    def __lt__(self, other):
        if hasattr(self, 'id') and hasattr(other, 'id'):
            return self.id.lower() < other.id.lower()
        else:
            return repr(self) < repr(other)


    def __le__(self, other):
        if hasattr(self, 'id') and hasattr(other, 'id'):
            return self.id.lower() <= other.id.lower()
        else:
            return repr(self) <= repr(other)


    def __cmp__(self, other):
        if hasattr(self, 'id') and hasattr(other, 'id'):
            return cmp(self.id.lower(), other.id.lower())
        else:
            return cmp(repr(self), repr(other))


    def __hash__(self):
        if self._hash:
            return self._hash
        if hasattr(self, 'id'):
            self._hash = hash(self.id)
        elif hasattr(self, '_json_data') and self._json_data:
            self._hash = hash(jsonlib.dumps(self._json_data))
        else:
            self._hash = hash(self)
        return self._hash
