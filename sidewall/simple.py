'''
journl.py: representation of a Dimensions journal record

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


class SimpleEntity(DimensionsCore):
    _attributes = ['id', 'name'] + DimensionsCore._attributes


    def _set_attributes(self, data, overwrite = False):
        if __debug__: log('setting attributes on {} using {}', id(self), data)
        set_objattr(self, 'id',   data.get('id', ''),    overwrite)
        set_objattr(self, 'name', data.get('name', ''), overwrite)


    def __repr__(self):
        return "<SimpleEntity {}>".format(self.id)
