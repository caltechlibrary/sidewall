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
        if not isinstance(data, dict):
            raise InternalError('Data not in dict format')
        super()._update_attributes(data)

        set_objattr = lambda attr, value: object.__setattr__(self, attr, value)
        set_objattr('affiliations', [])

        if 'affiliations' in data:
            objattr = lambda attr: object.__getattribute__(self, attr)
            affiliations = objattr('affiliations')
            for org in data['affiliations']:
                affiliations.append(Organization(org))


    def __repr__(self):
        return "<Author {}: '{} {}'>".format(self.id, self.first_name, self.last_name)
