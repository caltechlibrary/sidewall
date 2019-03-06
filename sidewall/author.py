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

from .debug import log
from .person import Person
from .organization import Organization
from .exceptions import *


# Example of an item returned in a publication's author_affiliations list:
#
# {'current_organization_id': '',
#  'first_name': 'Stefanie',
#  'last_name': 'Wehner',
#  'orcid': '',
#  'researcher_id': '',
#  'affiliations': [{'city': 'Munich',
#                    'city_id': 2867714,
#                    'country': 'Germany',
#                    'country_code': 'DE',
#                    'id': 'grid.419548.5',
#                    'name': 'Max Planck Institute of Psychiatry',
#                    'state': None,
#                    'state_code': None}],
# },

class Author(Person):
    _new_attributes = ['affiliations']
    _attributes = _new_attributes + Person._attributes


    def _update_attributes(self, data):
        if __debug__: log('updating object {} using {}', id(self), data)
        if not isinstance(data, dict):
            raise InternalError('Data not in dict format')
        super()._update_attributes(data)

        objattr = lambda attr: object.__getattribute__(self, attr)
        set_objattr = lambda attr, value: object.__setattr__(self, attr, value)

        try:
            affiliations = objattr('affiliations')
        except:
            affiliations = []
        if 'affiliations' in data:
            dimensions = objattr('_dimensions')
            if dimensions:
                for org in data['affiliations']:
                    affiliations.append(dimensions.factory(Organization, org, self))
            else:
                for org in data['affiliations']:
                    affiliations.append(Organization(org, self))
        set_objattr('affiliations', affiliations)


    def __repr__(self):
        return "<Author {}: '{} {}'>".format(self.id, self.first_name, self.last_name)
