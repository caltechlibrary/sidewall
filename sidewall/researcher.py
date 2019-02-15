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

from .debug import log
from .person import Person
from .organization import Organization
from .exceptions import *

class Researcher(Person):
    _attributes = ['affiliations'] + Person._attributes

    def _update_attributes(self, data):
        if __debug__: log('updating object {} using {}', id(self), data)
        if not isinstance(data, dict):
            raise InternalError('Data not in dict format')
        super()._update_attributes(data)

        set_objattr = object.__setattr__
        set_objattr(self, 'affiliations', [])
        if 'research_orgs' in data:
            objattr = object.__getattribute__
            aff = objattr(self, 'affiliations')
            for org_id in data['research_orgs']:
                aff.append(Organization({'id': org_id}))


    def __repr__(self):
        return "<Researcher {}: '{} {}'>".format(self.id, self.first_name,
                                                 self.last_name)
