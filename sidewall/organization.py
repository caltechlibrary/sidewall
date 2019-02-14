'''
organization.py: representation of an organization record

Authors
-------

Michael Hucka <mhucka@caltech.edu> -- Caltech Library

Copyright
---------

Copyright (c) 2019 by the California Institute of Technology.  This code is
open-source software released under a 3-clause BSD license.  Please see the
file "LICENSE" for more information.
'''

from .core import DimensionsCore, dimensions_search
from .debug import log
from .exceptions import *

# search publications where research_orgs.id="grid.214458.e"
#     return research_orgs limit 1
#
# gives:
#
# # {2 items
# "research_orgs":[1 item
# 0:{5 items
# "id":"grid.214458.e"
# "count":225580
# "acronym":"UM"
# "name":"University of Michigan"
# "country_name":"United States"
# }
# ]
# "_stats":{1 item
# "total_count":225580
# }
# }


class Organization(DimensionsCore):
    _attributes = ['acronym', 'city', 'city_id', 'country', 'country_code',
                   'country_name', 'id', 'name', 'state', 'state_code']

    _search_tmpl = 'publications where research_orgs.id="{}" return research_orgs limit 1'


    def _update_attributes(self, data):
        if __debug__: log('updating object {} using {}', id(self), data)
        if not isinstance(data, dict):
            raise InternalError('Data not in dict format')
        super()._update_attributes(data)

        set_objattr = object.__setattr__
        set_objattr(self, 'acronym', data.get('acronym', ''))
        set_objattr(self, 'city', data.get('city', ''))
        set_objattr(self, 'city_id', data.get('city_id', ''))
        set_objattr(self, 'country', data.get('country', ''))
        set_objattr(self, 'country_code', data.get('country_code', ''))
        set_objattr(self, 'country_name', data.get('country_name', ''))
        set_objattr(self, 'id', data.get('id', ''))
        set_objattr(self, 'name', data.get('name', ''))
        set_objattr(self, 'state', data.get('state', ''))
        set_objattr(self, 'state_code', data.get('state_code', ''))


    def _fill_record(self, json):
        # Be careful not to invoke "self.x" b/c it causes infinite recursion.
        if __debug__: log('filling object {} using {}', id(self), json)
        if 'research_orgs' in json:
            update = object.__getattribute__(self, '_update_attributes')
            update(json['research_orgs'][0])


    def __repr__(self):
        return "<Organization {}: '{}'>".format(self.id, self.name)
