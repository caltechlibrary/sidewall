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
from .exceptions import *


class Journal(DimensionsCore):
    _attributes = ['id', 'title'] + DimensionsCore._attributes


    def _update_attributes(self, data):
        super()._update_attributes(data)

        # https://docs.dimensions.ai/dsl/data.html#data
        self.title = data.get('title', '')
        self.id    = data.get('id', '')


    def __repr__(self):
        return "<Journal {}>".format(self.id)
