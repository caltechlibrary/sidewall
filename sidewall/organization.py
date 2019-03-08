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

from .core import DimensionsCore
from .data_helpers import objattr, set_objattr
from .debug import log
from .exceptions import *


class Organization(DimensionsCore):
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
        if __debug__: log('filling object {} using {}', id(self), data)
        # Update any missing fields
        set_attributes = objattr(self, '_set_attributes')
        set_attributes(data, overwrite = False)


    def __repr__(self):
        return "<Organization {}>".format(self.id)
