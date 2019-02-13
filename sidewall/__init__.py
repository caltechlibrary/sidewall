'''
sidewall: a library for programming with the Dimensions API

Authors
-------

Michael Hucka <mhucka@caltech.edu> -- Caltech Library

Copyright
---------

Copyright (c) 2019 by the California Institute of Technology.  This code is
open-source software released under a 3-clause BSD license.  Please see the
file "LICENSE" for more information.
'''

from .__version__  import __version__, __title__, __description__, __url__
from .__version__  import __author__, __email__
from .__version__  import __license__, __copyright__

from .exceptions   import *
from .author       import Author
from .dimensions   import Dimensions
from .organization import Organization
from .person       import Person
from .publication  import Publication
from .researcher   import Researcher
