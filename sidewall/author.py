'''
author.py: representation of an author record

Author class objects are returned when returning publication results, and
in those cases, the list of a person's affiliations will reflect their
affiliations with respect to a particular publication.

Authors
-------

Michael Hucka <mhucka@caltech.edu> -- Caltech Library

Copyright
---------

Copyright (c) 2019 by the California Institute of Technology.  This code is
open-source software released under a 3-clause BSD license.  Please see the
file "LICENSE" for more information.
'''

from .data_helpers import objattr, set_objattr, new_object
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


    def _lazy_expand(self, data):
        # Be careful not to invoke "self.x" b/c it causes infinite recursion.
        super()._lazy_expand(data)
        if __debug__: log('expanding attributes on {} using {}', id(self), data)
        affiliations = objattr(self, 'affiliations', [])
        dimensions = objattr(self, '_dimensions', None)
        for org_data in data.get('affiliations', []):
            affiliations.append(new_object(Organization, org_data, dimensions, self))
        set_objattr(self, 'affiliations', affiliations, overwrite = False)
        # Special case: we do not fill author affiliations beyond what shows
        # up for given publication, so we mark it as done at this point.
        mark_done = objattr(self, '_mark_done')
        mark_done('affiliations')
