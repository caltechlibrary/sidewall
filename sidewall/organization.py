'''
organization.py: representation of an organization record

Sidewall uses the object class 'Organization' to represent an organization in
results returned by Dimensions.  In Sidewall, the set of fields possessed by
an 'Organization' is the union of all fields that Dimensions provides in
different contexts for organizations.  For example, the information about
organizations included in an author's affiliation list in a publication is
somewhat different from what is provided if a search ending in `return
research_orgs` is used.  Sidewall makes the assumption that an organization
with a given organization identifier ("grid id") is the same organization no
matter the context in which it is mentioned in a search result, and so
Sidewall smooths over the field differences and queries Dimensions behind the
scenes to get missing values when it can (and when they exist).

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
from .data_helpers import objattr, set_objattr
from .debug import log
from .persistable import Persistable


class Organization(DimensionsCore, Persistable):
    _new_attributes = ['acronym', 'city', 'city_id', 'country', 'country_code',
                       'country_name', 'id', 'name', 'state', 'state_code']
    _attributes     = _new_attributes + DimensionsCore._attributes
    _search_tmpl    = 'publications where research_orgs.id="{}" return research_orgs'


    def _set_attributes(self, data, overwrite = False):
        if __debug__: log('setting attributes on {} using {}', id(self), data)
        set_objattr(self, 'acronym',      data.get('acronym', ''),      overwrite)
        set_objattr(self, 'city',         data.get('city', ''),         overwrite)
        set_objattr(self, 'city_id',      data.get('city_id', ''),      overwrite)
        set_objattr(self, 'country',      data.get('country', ''),      overwrite)
        set_objattr(self, 'country_code', data.get('country_code', ''), overwrite)
        set_objattr(self, 'country_name', data.get('country_name', ''), overwrite)
        set_objattr(self, 'id',           data.get('id', ''),           overwrite)
        set_objattr(self, 'name',         data.get('name', ''),         overwrite)
        set_objattr(self, 'state',        data.get('state', ''),        overwrite)
        set_objattr(self, 'state_code',   data.get('state_code', ''),   overwrite)


    def _fill_record(self, data):
        # Be careful not to invoke "self.x" b/c it causes infinite recursion.
        if __debug__: log('filling object {} using {}', id(self), data)
        # Update any missing fields
        set_attributes = objattr(self, '_set_attributes')
        set_attributes(data, overwrite = False)
