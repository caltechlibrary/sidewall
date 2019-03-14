'''
category.py: base class for category entities

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


class Category(SimpleEntity, Persistable):
    pass
