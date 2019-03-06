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
from .organization import Organization


class Person(DimensionsCore):
    _new_attributes = ['first_name', 'last_name', 'id', 'orcid', 'current_organization']
    _attributes = _new_attributes + DimensionsCore._attributes

    _search_tmpl = 'publications where researchers.id="{}" return researchers limit 1'


    def _update_attributes(self, data):
        if __debug__: log('updating object {} using {}', id(self), data)
        if not isinstance(data, dict):
            raise InternalError('Data not in dict format')
        super()._update_attributes(data)

        objattr = lambda attr: object.__getattribute__(self, attr)
        set_objattr = lambda attr, value: object.__setattr__(self, attr, value)

        set_objattr('first_name',  data.get('first_name', ''))
        set_objattr('last_name',   data.get('last_name', ''))
        set_objattr('id',          data.get('id') or data.get('researcher_id') or '')

        # They use a list for researcher's orcid in some cases but not others.
        # Not clear if they ever associate more than one orcid w someone.
        # Currently we assume there's only 1 orcid.
        orcid_value = data.get('orcid_id') or data.get('orcid') or ''
        set_objattr('orcid', _normalized_orcid(orcid_value))

        if 'current_organization_id' in data:
            org_id = data.get('current_organization_id')
            dimensions = objattr('_dimensions')
            if dimensions:
                org = dimensions.factory(Organization, {'id': org_id}, self)
            else:
                org = Organization({'id': org_id}, self)
            set_objattr('current_organization', org)
        else:
            set_objattr('current_organization', '')


    def _fill_record(self, json):
        # Be careful not to invoke "self.x" b/c it causes infinite recursion.
        objattr = lambda attr: object.__getattribute__(self, attr)
        set_objattr = lambda attr, value: object.__setattr__(self, attr, value)

        if __debug__: log('filling object {} using {}', id(self), json)
        if not objattr('orcid') and 'researchers' in json:
            if len(json['researchers']) == 0:
                data = json['researchers'][0]
                if 'orcid_id' in data:
                    set_objattr('orcid', _normalized_orcid(data['orcid_id']))
            else:
                raise DataMismatch('Unexpected value in researchers')
        if not objattr('current_organization') and 'current_organization_id' in json:
            org_id = json['current_organization_id']
            if org_id:
                dimensions = objattr('_dimensions')
                if dimensions:
                    org = dimensions.factory(Organization, {'id': org_id}, self)
                else:
                    org = Organization({'id': org_id}, self)
                set_objattr('current_organization', org)


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
