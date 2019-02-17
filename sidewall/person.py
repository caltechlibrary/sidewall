'''
person.py: base class for people records in Sidewall

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
from .exceptions import *

# Example of researchers blob from using "return researchers":
#
# { 'id': 'ur.0665132124.52',
#   'count': 68,
#   'first_name': 'Michael',
#   'last_name': 'Hucka',
#   'orcid_id': ['0000-0001-9105-5960'],
#   'research_orgs': [ 'grid.214458.e',
#                      'grid.20861.3d',
#                      'grid.10392.39',
#                    ],
# },
#
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

class Person(DimensionsCore):
    _attributes = ['first_name', 'last_name', 'id', 'orcid'] + DimensionsCore._attributes

    _search_tmpl = 'publications where researchers.id="{}" return researchers limit 1'


    def _update_attributes(self, data):
        if __debug__: log('updating object {} using {}', id(self), data)
        if not isinstance(data, dict):
            raise InternalError('Data not in dict format')
        super()._update_attributes(data)

        objattr = lambda attr: object.__getattribute__(self, attr)
        set_objattr = lambda attr, value: object.__setattr__(self, attr, value)

        set_objattr('first_name', data.get('first_name', ''))
        set_objattr('last_name',  data.get('last_name', ''))
        set_objattr('id',         data.get('id') or data.get('researcher_id') or '')

        # They use a list for researcher's orcid in some cases but not others.
        # Not clear if they ever associate more than one orcid w someone.
        # Currently we assume there's only 1 orcid.
        set_objattr('orcid', data.get('orcid_id') or data.get('orcid') or '')
        orcid = objattr('orcid')
        if isinstance(orcid, list):
            if len(orcid) > 1:
                raise DataMismatch('More than one ORCID id for {} {} ({})'
                                   .format(self.first_name, self.last_name, self.id))
            set_objattr('orcid', orcid[0])


    def _fill_record(self, json):
        # Be careful not to invoke "self.x" b/c it causes infinite recursion.
        if __debug__: log('filling object {} using {}', id(self), json)
        if 'researchers' in json:
            update = object.__getattribute__(self, '_update_attributes')
            update(json['researchers'][0])


    def __repr__(self):
        return "<Person {}: '{} {}'>".format(self.id, self.first_name, self.last_name)
