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


# Classes
# .............................................................................

class DimensionsCore(object):
    _attributes = []

    def __init__(self, json, creator = None, dimensions_obj = None):
        self._json_data = json          # A dict.
        self._searched = set({'id'})    # Attributes we have searched for.
        self._hash = None
        self._dimensions = None
        self._attributes_updated = False

        if dimensions_obj:
            self._dimensions = dimensions_obj
        elif isinstance(creator, DimensionsCore):
            self._dimensions = creator._dimensions
        elif creator:
            self._dimensions = creator

        # Try to set the id here, since all Dimensions objects seem to have one.
        # The remaining attributes are set in a lazy way via __getattr__.
        dim_id = json.get('id') or json.get('researcher_id') or ''
        object.__setattr__(self, 'id', dim_id)
        if __debug__: log('object {} has Dimensions id "{}"', id(self), dim_id)


    def __getattr__(self, attr):
        # Implements lazy filling in of attribute values.  Note that Python
        # calls __getattr__ on attribute lookups where the attribute is not
        # yet defined on an object.  Thus, the logic below assumes that the
        # attribute doesn't exist yet on this object.

        # Be careful not to invoke "self.x" b/c it causes infinite recursion.
        # Make every attribute lookup use object.__getattribute__.
        objattr = lambda attr: object.__getattribute__(self, attr)
        set_objattr = lambda attr, value: object.__setattr__(self, attr, value)

        if attr in objattr('_attributes') and not objattr('_attributes_updated'):
            if __debug__: log('lookup of {} on {} triggering update', attr, id(self))
            set_objattr('_attributes_updated', True)
            updater = objattr('_update_attributes')
            updater(objattr('_json_data'))
        return objattr(attr)


    def __getattribute__(self, attr):
        # Be careful not to invoke "self.x" b/c it causes infinite recursion.
        # Make every attribute lookup use object.__getattribute__.
        objattr = lambda attr: object.__getattribute__(self, attr)
        set_objattr = lambda attr, value: object.__setattr__(self, attr, value)

        if __debug__: log('looking up "{}" on object {}', attr, id(self))
        if not attr in objattr('_attributes'):
            raise AttributeError(attr)
        if not (objattr(attr) or attr in objattr('_searched')):
            if __debug__: log('"{}" not yet set on object {}', attr, id(self))
            # Attribute has no value and we haven't tried searching for it.
            # We now set the flag that we tried, whether we can search or not.
            searched = objattr('_searched')
            searched.add(attr)      # Warning: don't combine this w/ next line.
            set_objattr('_searched', searched)
            # All the methods for this approach need a Dimensions id.
            dim_id = objattr('id')
            if not dim_id:
                if __debug__: log("missing id -- can't search for \"{}\"", attr)
                return objattr(attr)
            try:
                # If we know of a way to expand values on this object, there
                # will be a class attribute providing a search template.
                search_tmpl = objattr('_search_tmpl')
            except:
                if __debug__: log("no search template -- can't fill in values")
            else:
                dim = objattr('_dimensions')
                search = object.__getattribute__(dim, 'record_search')
                record_json = search(search_tmpl, dim_id)
                # Subclasses may have their own _fill_record.  Look for all.
                classes = inspect.getmro(self.__class__)
                for c in classes[:-1]:  # Skip class 'object'.
                    try:
                        fill_record = object.__getattribute__(c, '_fill_record')
                        if __debug__: log('using _fill_record on {}', str(c))
                        fill_record(self, record_json)
                    except:
                        pass
        return objattr(attr)


    def _update_attributes(self, json):
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
