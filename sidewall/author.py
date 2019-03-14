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

from .data_helpers import objattr, set_objattr
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
#
# However, entries can be very sparse too.  Here's another example:
# {"current_organization_id": "",
#  "researcher_id": "",
#  "first_name": "Brittany",
#  "last_name": "Dahlen",
#  "affiliations": [{"name": "Children's Minnesota, Minneapolis, MN, USA 55404"}],
#  "orcid": ""
#  }


class Author(Person):
    _new_attributes = ['affiliations']
    _attributes     = _new_attributes + Person._attributes


    def _set_attributes(self, data, overwrite = False):
        super()._set_attributes(data, overwrite = False)
        if __debug__: log('setting attributes on {} using {}', id(self), data)


    def _expand_attributes(self, data):
        super()._expand_attributes(data)
        if __debug__: log('expanding attributes on {} using {}', id(self), data)
        affiliations = objattr(self, 'affiliations', [])
        if 'affiliations' in data:
            dimensions = objattr(self, '_dimensions')
            if dimensions:
                for org in data['affiliations']:
                    affiliations.append(dimensions.factory(Organization, org, self))
            else:
                for org in data['affiliations']:
                    affiliations.append(Organization(org, self))
        set_objattr(self, 'affiliations', affiliations, overwrite = False)
        # Special case: we do not fill author affiliations beyond what shows
        # up for given publication, so we mark it as done at this point.
        mark_done = objattr(self, '_mark_done')
        mark_done('affiliations')


    def __repr__(self):
        return "<Author {}: '{} {}'>".format(self.id, self.first_name, self.last_name)
