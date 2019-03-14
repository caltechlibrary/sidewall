'''
country.py: base class for country entities

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
from .simple import SimpleEntity


class Country(SimpleEntity):
    def __repr__(self):
        return "<Country {}>".format(self.id)
