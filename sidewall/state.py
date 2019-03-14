'''
state.py: base class for state entities

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


class State(SimpleEntity):
    def __repr__(self):
        return "<State {}>".format(self.id)
