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
from .data_helpers import objattr, set_objattr
from .debug import log
from .exceptions import *
from .organization import Organization
from .person import Person


class Researcher(Person):
    _new_attributes = ['affiliations']
    _attributes = _new_attributes + Person._attributes


    def __init__(self, data):
        if isinstance(data, Author):
            # We're given an author object, probably obtained from a pub search,
            # and we want to fill it out to create a Researcher object.
            if __debug__: log('converting Author {} to Researcher', id(data))
            super().__init__(data._orig_data, creator = data)
            for attr in objattr(self, '_new_attributes'):
                setattr(self, attr, getattr(data, attr))
        else:
            # This is a standard initialization, not a case of upconverting.
            super().__init__(data)


    def _expand_attributes(self, data):
        super()._expand_attributes(data)
        if __debug__: log('expanding attributes on {} using {}', id(self), data)
        if 'research_orgs' in data:
            try:
                affiliations = objattr(self, 'affiliations')
            except:
                affiliations = []
            dimensions = objattr(self, '_dimensions')
            if dimensions:
                for org_id in data['research_orgs']:
                    affiliations.append(dimensions.factory(Organization, {'id': org_id}, self))
            else:
                for org_id in data['research_orgs']:
                    affiliations.append(Organization({'id': org_id}, self))
            set_objattr(self, 'affiliations', affiliations, overwrite = True)


    def _fill_record(self, data):
        # Be careful not to invoke "self.x" b/c it causes infinite recursion.
        if __debug__: log('filling object {} using {}', id(self), data)
        if 'research_orgs' not in data or len(data['research_orgs']) == 0:
            return
        affiliations = objattr(self, 'affiliations')
        dimensions = objattr(self, '_dimensions')
        if dimensions:
            for org_id in data['research_orgs']:
                affiliations.append(dimensions.factory(Organization, {'id': org_id}, self))
        else:
            for org_id in data['research_orgs']:
                affiliations.append(Organization({'id': org_id}, self))
        set_objattr(self, 'affiliations', affiliations, overwrite = True)


    def __repr__(self):
        return "<Researcher {}: '{} {}'>".format(self.id, self.first_name,
                                                 self.last_name)
