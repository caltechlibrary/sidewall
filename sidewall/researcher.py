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
from .debug import log
from .exceptions import *
from .organization import Organization
from .person import Person


class Researcher(Person):
    _attributes = ['affiliations'] + Person._attributes

    def __init__(self, data):
        if isinstance(data, Author):
            # We're given an author object, probably obtained from a pub search,
            # and we want to fill it out to create a Researcher object.
            if __debug__: log('converting Author {} to Researcher', id(data))
            super().__init__(data.__dict__)
        else:
            # This is a standard initialization, not a case of upconverting.
            super().__init__(data)


    def _update_attributes(self, data):
        if __debug__: log('updating object {} using {}', id(self), data)
        if not isinstance(data, dict):
            raise InternalError('Data not in dict format')
        super()._update_attributes(data)

        set_objattr = lambda attr, value: object.__setattr__(self, attr, value)
        set_objattr('affiliations', [])

        if 'research_orgs' in data:
            objattr = lambda attr: object.__getattribute__(self, attr)
            affiliations = objattr('affiliations')
            for org_id in data['research_orgs']:
                affiliations.append(Organization({'id': org_id}))


    def __repr__(self):
        return "<Researcher {}: '{} {}'>".format(self.id, self.first_name,
                                                 self.last_name)
