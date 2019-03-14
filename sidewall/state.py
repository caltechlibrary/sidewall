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

from .simple import SimpleEntity
from .persistable import Persistable


class State(SimpleEntity, Persistable):
    pass
