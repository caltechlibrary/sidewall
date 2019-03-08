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
from .data_helpers import objattr, set_objattr, dimensions_id
from .debug import log
from .exceptions import *
from .organization import Organization


class Person(DimensionsCore):
    _new_attributes = ['first_name', 'last_name', 'id', 'orcid', 'current_organization']
    _attributes     = _new_attributes + DimensionsCore._attributes
    _search_tmpl    = 'publications where researchers.id="{}" return researchers limit 1'


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


    def _expand_attributes(self, data):
        if __debug__: log('expanding attributes on {} using {}', id(self), data)
        if 'current_organization_id' in data:
            org_id = data.get('current_organization_id')
            dimensions = objattr(self, '_dimensions')
            if dimensions:
                org = dimensions.factory(Organization, {'id': org_id}, self)
            else:
                org = Organization({'id': org_id}, self)
            set_objattr(self, 'current_organization', org)
        else:
            set_objattr(self, 'current_organization', '')


    def _fill_record(self, json):
        if __debug__: log('filling object {} using {}', id(self), json)
        if not objattr(self, 'orcid') and 'researchers' in json:
            if len(json['researchers']) == 0:
                data = json['researchers'][0]
                if 'orcid_id' in data:
                    set_attributes = objattr(self, '_set_attributes')
                    set_attributes(data)
            else:
                raise DataMismatch('Unexpected value in researchers')
        if not objattr(self, 'current_organization') and 'current_organization_id' in json:
            org_id = json['current_organization_id']
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
