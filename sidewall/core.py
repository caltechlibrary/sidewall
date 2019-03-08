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

import inspect
import json as jsonlib

from .debug import log
from .data_helpers import dimensions_id, objattr, set_objattr


# Classes
# .............................................................................
#
# When an object is first created, the goal is to set only a minimum number
# of attributes here, and delay calling the _expand_attributes() methods
# until additional fields are necessary.  The basic scheme is this:
#
# - Every class has a _set_attributes() method that sets the scalar attributes.
#
# - Classes that have more elaborate attributes (such as lists of other
#   objects) have the method _expand_attributes().  This gets called by
#   __getattribute__(), defined below, upon the first time an elaborate
#   attribute is accessed.  The core object attribute _attributes_expanded is
#   set by __getattribute__() to mark that the method _expand_attributes()
#   has been called, so that it's not called again.
#
# - Attribute values are not always filled in because the search results from
#   Dimensions aren't always complete.  In some cases, we have a way to query
#   Dimensions in a different way to get additional field values.  The logic
#   for doing the secondary search is also in __getattribute__() below.

class DimensionsCore(object):
    _attributes = []

    def __init__(self, data, creator = None, dimensions_obj = None):
        if not isinstance(data, dict):
            raise InternalError('Data not in dict format')
        self._json_data = data         # A dict.
        self._search_data = None       # If we search, we store it for debugging
        self._hash = None
        self._dimensions = None
        self._attributes_expanded = False
        self._attributes_done = set()  # Attributes we have finished filling.

        if dimensions_obj:
            self._dimensions = dimensions_obj
        elif isinstance(creator, DimensionsCore):
            self._dimensions = creator._dimensions
        elif creator:
            self._dimensions = creator

        self._set_attributes(data, overwrite = True)
        self._mark_done_attributes()


    def __getattribute__(self, attr):
        if not attr in objattr(self, '_attributes'):
            return objattr(self, attr)
        attrib_dict = objattr(self, '__dict__')
        if not (attr in attrib_dict or objattr(self, '_attributes_expanded')):
            # Attribute has no value, but we haven't expanded all attributes.
            if __debug__: log('"{}" hasn\'t been set yet', attr)
            expand_attributes = objattr(self, '_expand_attributes')
            expand_attributes(objattr(self, '_json_data'))
            set_objattr(self, '_attributes_expanded', True)
        if not (objattr(self, attr) or attr in objattr(self, '_attributes_done')):
            # Attribute still has no value, but we haven't tried searching yet.
            # All the methods for this approach need a Dimensions id.
            dim_id = objattr(self, 'id')
            if dim_id:
                if __debug__: log('still missing value for "{}" on {}', attr, id(self))
                try:
                    # If we know of a way to expand values on this object, there
                    # will be a class attribute providing a search template.
                    search_tmpl = objattr(self, '_search_tmpl')
                except:
                    if __debug__: log("no search template -- can't fill in values")
                else:
                    dim = objattr(self, '_dimensions')
                    if dim:
                        search = objattr(dim, 'record_search')
                        search_results = search(search_tmpl, dim_id)
                        # Save what we got back in case we need to debug things.
                        set_objattr(self, '_search_data', search_results)
                        # Subclasses may have their own _fill_record.  Look for all.
                        classes = inspect.getmro(self.__class__)
                        for c in classes[:-1]:  # Skip class 'object'.
                            try:
                                fill_record = objattr(c, '_fill_record')
                                fill_record(self, search_results)
                            except:
                                pass
            else:
                if __debug__: log("missing id -- can't search for \"{}\"", attr)
            # We now set the flag that we tried, whether we can search or not.
            mark_done = objattr(self, '_mark_done')
            mark_done(attr)
        value = objattr(self, attr)
        if __debug__: log('returning "{}" for "{}" on {}', value, attr, id(self))
        return value


    def _mark_done(self, attr):
        if __debug__: log('marking "{}" as final on {}', attr, id(self))
        done = objattr(self, '_attributes_done')
        done.add(attr)                  # Don't combine this with next line.
        set_objattr(self, '_attributes_done', done)


    def _mark_done_attributes(self):
        # Mark attributes that have been set AND have a non-null value.
        done = objattr(self, '_attributes_done')
        for attr in objattr(self, '_attributes'):
            if attr in self.__dict__ and objattr(self, attr):
                done.add(attr)
        if __debug__: log('updated _attributes_done list on {}: {}', id(self), done)
        set_objattr(self, '_attributes_done', done)


    def _set_attributes(self, json, overwrite = True):
        '''Method stub for subclasses to override.'''
        pass


    def _expand_attributes(self, json):
        '''Method stub for subclasses to override.'''
        pass


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
