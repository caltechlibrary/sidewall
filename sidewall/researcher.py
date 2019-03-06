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


# Example of a "researchers" blob from using "return researchers":
#
# 'researchers': [{ 'id': 'ur.0665132124.52',
#                   'count': 68,
#                   'first_name': 'Michael',
#                   'last_name': 'Hucka',
#                   'orcid_id': ['0000-0001-9105-5960'],
#                   'research_orgs': [ 'grid.214458.e',
#                                      'grid.20861.3d',
#                                      'grid.10392.39',
#                                    ]}]

class Researcher(Person):
    _new_attributes = ['affiliations']
    _attributes = _new_attributes + Person._attributes


    def __init__(self, data):
        if isinstance(data, Author):
            # We're given an author object, probably obtained from a pub search,
            # and we want to fill it out to create a Researcher object.
            if __debug__: log('converting Author {} to Researcher', id(data))
            super().__init__(data._json_data, creator = data)
            for attr in object.__getattribute__(self, '_new_attributes'):
                setattr(self, attr, getattr(data, attr))
        else:
            # This is a standard initialization, not a case of upconverting.
            super().__init__(data)


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
        if 'research_orgs' in data:
            dimensions = objattr('_dimensions')
            if dimensions:
                for org_id in data['research_orgs']:
                    affiliations.append(dimensions.factory(Organization, {'id': org_id}, self))
            else:
                for org_id in data['research_orgs']:
                    affiliations.append(Organization({'id': org_id}, self))
        set_objattr('affiliations', affiliations)


    def _fill_record(self, json):
        # Be careful not to invoke "self.x" b/c it causes infinite recursion.
        objattr = lambda attr: object.__getattribute__(self, attr)
        if __debug__: log('filling object {} using {}', id(self), json)
        if not objattr('affiliations') and 'researchers' in json:
            data = json['researchers'][0]
            if 'research_orgs' not in data or len(data['research_orgs']) == 0:
                return
            affiliations = objattr('affiliations')
            dimensions = objattr('_dimensions')
            if dimensions:
                for org_id in data['research_orgs']:
                    affiliations.append(dimensions.factory(Organization, {'id': org_id}, self))
            else:
                for org_id in data['research_orgs']:
                    affiliations.append(Organization({'id': org_id}, self))


    def __repr__(self):
        return "<Researcher {}: '{} {}'>".format(self.id, self.first_name,
                                                 self.last_name)
