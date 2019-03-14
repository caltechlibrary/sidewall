'''
persistable.py: mixin class to identify objects that can be persisted

Some of the results returned by a Dimensions query must be interpreted in
the context of that query, and caching the results across queries would be
bad.  This class is a Python mixin meant to be added to definitions of
classes that can be persisted in Sidewall.

Authors
-------

Michael Hucka <mhucka@caltech.edu> -- Caltech Library

Copyright
---------

Copyright (c) 2019 by the California Institute of Technology.  This code is
open-source software released under a 3-clause BSD license.  Please see the
file "LICENSE" for more information.
'''

class Persistable(object):
    persistable = True
