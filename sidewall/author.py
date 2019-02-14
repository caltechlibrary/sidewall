'''
author.py: representation of an author record

Authors
-------

Michael Hucka <mhucka@caltech.edu> -- Caltech Library

Copyright
---------

Copyright (c) 2019 by the California Institute of Technology.  This code is
open-source software released under a 3-clause BSD license.  Please see the
file "LICENSE" for more information.
'''

from .core import DimensionsCore
from .debug import log
from .person import Person
from .organization import Organization
from .exceptions import *

# search publications where researchers.id="ur.01224076035.43" return researchers


class Author(Person):
    _attributes = ['affiliations'] + Person._attributes

    def _update_attributes(self, data):
        if __debug__: log('updating object {} using {}', id(self), data)
        super()._update_attributes(data)

        set_objattr = object.__setattr__
        set_objattr(self, 'affiliations', [])
        if 'affiliations' in data:
            objattr = object.__getattribute__
            aff = objattr(self, 'affiliations')
            for org_id in data['affiliations']:
                aff.append(Organization({'id': org_id}))


    def __repr__(self):
        return "<Author {}: '{} {}'>".format(self.id, self.first_name, self.last_name)
