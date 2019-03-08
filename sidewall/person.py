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
from .data_helpers import objattr, set_objattr, dimensions_id, matching_record
from .debug import log
from .exceptions import *
from .organization import Organization


# A frustrating discovery has been that searching Dimensions with
#     search publications where researchers.id="{}" return researchers limit 1
# does NOT necessarily return the researcher that is identified by the id
# value in the argument.  (You would think that the first result would be the
# same researcher, but no.)  It turns out we have to iterate over multiple
# results and match the researcher id's to find the right record.
#
# So, that's the explanation for why the search template returns many results
# instead of a single one, and why _fill_record() iterates the way it does.

class Person(DimensionsCore):
    _new_attributes = ['first_name', 'last_name', 'id', 'orcid', 'current_organization']
    _attributes     = _new_attributes + DimensionsCore._attributes
    _search_tmpl    = 'publications where researchers.id="{}" return researchers'


    def _set_attributes(self, data, overwrite = False):
        if __debug__: log('setting attributes on {} using {}', id(self), data)
        set_objattr(self, 'first_name',  data.get('first_name', ''), overwrite)
        set_objattr(self, 'last_name',   data.get('last_name', ''),  overwrite)
        set_objattr(self, 'id',          dimensions_id(data),        overwrite)

        # Dimensions uses a list for researcher's orcid in some cases but not
        # others.  Why?  Not clear if they ever associate more than one orcid
        # w someone.  Currently we assume there's never more than 1 orcid.
        orcid_value = data.get('orcid_id') or data.get('orcid') or ''
        set_objattr(self, 'orcid', _normalized_orcid(orcid_value), overwrite)


    # When _expand_attributes() gets called, it will be with a record for a
    # researcher, which looks like this example.  We use Note that the current
    # organization shows up in both current_organization_id and the list of
    # affiliations.  We fish out the data in the list of affiliations and hand
    # that to the creation of an Organization object for the current org field.
    #
    #    {'current_organization_id': 'grid.184769.5',
    #     'first_name': 'Arunima K.',
    #     'last_name': 'Singh',
    #     'orcid': "['0000-0002-7212-6310']",
    #     'researcher_id': 'ur.01137756010.32',
    #     'affiliations': [{'country': 'United States',
    #                       'state_code': 'US-CA',
    #                       'city': 'Berkeley',
    #                       'city_id': 5327684,
    #                       'id': 'grid.184769.5',
    #                       'country_code': 'US',
    #                       'state': 'California',
    #                       'name': 'Lawrence Berkeley National Laboratory'}]}

    def _expand_attributes(self, data):
        super()._expand_attributes(data)
        if __debug__: log('expanding attributes on {} using {}', id(self), data)
        if 'current_organization_id' in data:
            org_id = data.get('current_organization_id')
            if org_id:
                # If there's an affiliations list, one of them might contain
                # richer info about the organization. Let's try to find it.
                if 'affiliations' in data:
                    org_record = matching_record(data, 'affiliations', org_id)
                if not org_record:
                    org_record = {'id': org_id}
                dimensions = objattr(self, '_dimensions')
                if dimensions:
                    org = dimensions.factory(Organization, org_record, self)
                else:
                    org = Organization(org_record, self)
                set_objattr(self, 'current_organization', org)
                return
        set_objattr(self, 'current_organization', None)


    def _fill_record(self, data):
        if __debug__: log('filling object {} using {}', id(self), data)
        if not objattr(self, 'orcid') and 'orcid_id' in data:
            set_attributes = objattr(self, '_set_attributes')
            set_attributes(data, overwrite = True)
        if not objattr(self, 'current_organization') and 'current_organization_id' in data:
            org_id = data['current_organization_id']
            if org_id:
                dimensions = objattr(self, '_dimensions')
                if dimensions:
                    org = dimensions.factory(Organization, {'id': org_id}, self)
                else:
                    org = Organization({'id': org_id}, self)
                set_objattr(self, 'current_organization', org)


    def __repr__(self):
        return "<Person {}: '{} {}'>".format(self.id, self.first_name, self.last_name)


def _normalized_orcid(value):
    if isinstance(value, str) and '[' in value:
        # I suspect there's a bug in how I store test cases, but let's
        # handle the case where a list was turned into a string.
        return value.strip("'[]")
    elif isinstance(value, list):
        if len(value) > 1:
            raise DataMismatch('More than one ORCID id: {}'.format(value))
        return value[0]
    else:
        return value
