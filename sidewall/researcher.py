'''
researcher.py: representation of an researcher record

Authors
-------

Michael Hucka <mhucka@caltech.edu> -- Caltech Library

Copyright
---------

Copyright (c) 2019 by the California Institute of Technology.  This code is
open-source software released under a 3-clause BSD license.  Please see the
file "LICENSE" for more information.
'''

from .author import Author
from .data_helpers import objattr, set_objattr, new_object
from .debug import log
from .exceptions import *
from .organization import Organization
from .person import Person


class Researcher(Person):
    _new_attributes = ['affiliations', 'role']
    _attributes = _new_attributes + Person._attributes


    def __init__(self, data, creator = None, dimensions_obj = None):
        if isinstance(data, Author):
            # We're given an author object, probably obtained from a pub search,
            # and we want to fill it out to create a Researcher object.
            if __debug__: log('converting Author {} to Researcher', id(data))
            dimensions = objattr(data, '_dimensions', None)
            super().__init__(data._orig_data, data, dimensions)
        else:
            # This is a standard initialization, not a case of upconverting.
            super().__init__(data, creator, dimensions_obj)


    def _lazy_expand(self, data):
        # Be careful not to invoke "self.x" b/c it causes infinite recursion.
        if __debug__: log('expanding attributes on {} using {}', id(self), data)
        super()._lazy_expand(data)
        # When researcher data comes from a grant, there may be a 'role' field.
        set_objattr(self, 'role', data.get('role', ''), overwrite = True)
        set_affiliations = objattr(self, '_set_affiliations')
        set_affiliations(data)


    def _fill_record(self, data):
        # Be careful not to invoke "self.x" b/c it causes infinite recursion.
        if __debug__: log('filling object {} using {}', id(self), data)
        set_affiliations = objattr(self, '_set_affiliations')
        set_affiliations(data)


    def _set_affiliations(self, data, field_name = 'research_orgs'):
        if field_name not in data or len(data[field_name]) == 0:
            return
        affiliations = objattr(self, 'affiliations', [])
        dimensions = objattr(self, '_dimensions', None)
        if isinstance(data[field_name][0], str):
            # Case 1: it's a list of grid id's.
            for org_id in data[field_name]:
                for existing_org in affiliations:
                    if org_id == existing_org.id:
                        # Nothing more to do, b/c all we have is the id.
                        break
                else: # This 'else' is for the inner 'for' loop, not the 'if' stmt.
                    affiliations.append(new_object(Organization, {'id': org_id}, dimensions, self))
        else:
            # Case 2: it's a list of dict's containing org field/value data.
            for org_data in data[field_name]:
                for existing_org in affiliations:
                    if org_data['id'] == existing_org.id:
                        existing_org._set_attributes(org_data, overwrite = False)
                        break
                else: # This 'else' is for the inner 'for' loop, not the 'if' stmt.
                    affiliations.append(new_object(Organization, org_data, dimensions, self))
        set_objattr(self, 'affiliations', affiliations, overwrite = True)
