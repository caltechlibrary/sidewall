'''
sidewall: a library for interacting with the Dimensions API

Dimensions offers a networked API and search language (the DSL).  However,
interacting with the DSL via the network API normally requires sending a
search string to the Dimensions server, then interpreting the JSON results
and handling various issues such as iterating to obtain more than 1000 values
(which requires the use of multiple queries), staying within API rate limits,
and more.  Sidewall ("Simple Dimensions wrapper client library") provides a
higher-level interface for working more conveniently with the Dimensions DSL
and network API.

Sidewall is meant to be used from other programs; it does not provide a
standalone command-line interface or graphical user interface.  At this time,
Sidewall only supports certain kinds of Dimensions queries and data results.

Basic setup
-----------

To use Sidewall, import the package and the symbol 'dimensions' in your
Python code:

    import sidewall
    from sidewall import dimensions

In case of problems, it may be useful to turn on debugging in Sidewall to see
everything that is happening behind the scenes.  You can do that by using
'set_debug()' after importing Sidewall:

    sidewall.set_debug(True)

To run queries, you will need first to have an account with Dimensions.
There are multiple ways of supplying user credentials to Sidewall.  The most
secure and more convenient way is to invoke the 'login()' method without any
arguments:

    dimensions.login()

When done this way, Sidewall will use the operating system's keyring/keychain
functionality to get the user name and password.  If the information does not
exist from a previous call to 'dimensions.login()', Sidewall will ask you for
the user name and password interactively, and then store it in the
keyring/keychain for next time.

If asking the user for credentials interactively on the command line is
unsuitable for the application you are writing, you can also supply a user
name and password to the 'login()' method as keyword arguments:

    dimensions.login(username = 'somelogin', password = 'somepassword')


Basic principles of running queries
-----------------------------------

Sidewall defines a method, 'query()', which you can use to run a search in
Dimensions and get back results.  The method takes a single argument, a
string.  Here is an example:

    pubs = dimensions.query('search publications for "SBML" return publications')

The 'query()' method returns an object that acts as a Python iterator -- you
can iterate over the results, use 'len()', and do other operations.  The
iterator will (if iterated) obtain all the results for a given Dimensions
query, up to the limit of 50,000 imposed by the Dimensions API.  If you want
to limit the number of results, set a value for the keyword argument
'limit_results' to 'query(...)'.  For example,

    pubs = dimensions.query('search publications for "SBML" return publications',
           limit_results = 1000)

The items returned by the iterator will be Sidewall objects of the kind
discussed in the section below on [Data mappings]().  The specific classes of
objects returned will correspond to the type of record expressed in the tail
end of the query handed to 'query()'.  For example, a query that ends in
'return publications' will produce Sidewall 'Publications' objects; a query
that ends in 'return researchers' will produce Sidewall 'Researcher' objects;
and so on.

Sidewall currently puts the following limitations on the form of the query
search string:

* it must begin with 'search'

* it must end with 'return publications', 'return researchers', or
  'return grants'

* it must only return a single type of thing (i.e., researchers or
  publications or grants)

* it must not put facet specifiers or limits on the returned results

* it must not use aggregation or other advanced DSL features

Data mappings
-------------

Sidewall defines object classes such as 'Researcher', 'Publication', and a
few others to represent the different types of entities returned as the
results of a Dimensions search query.  Sidewall's objects attempt to smooth
over some of the confusing aspects of the data representations in Dimensions
by providing single objects that consolidate different fields and facets of
the same underlying "thing".  Further, the fields of an object sometimes are
not available from a given query Dimensions performed by the user but may be
available if a different kind of query is performed; Sidewall uses this
knowledge in some cases to expand object field values automatically and
behind the scenes as needed.

The following data classes are defined by Sidewall at this time; note that
this is not all the types of data that Dimensions provides today, but future
work may improve Sidewall's coverage.

* 'Person', with subclasses 'Authors' and 'Researchers'
* 'Organization'
* 'Publication'
* 'Journal'
* 'Grant'
* several very simple objects: 'Category', 'City', 'Country', 'State'

For more information about the data objects and their attributes, please
refer to the GitHub page at https://github.com/caltechlibrary/sidewall/.

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
from .debug        import set_debug
from .dimensions   import dimensions, queryresults

from .author       import Author
from .category     import Category
from .city         import City
from .country      import Country
from .grant        import Grant
from .journal      import Journal
from .organization import Organization
from .person       import Person
from .publication  import Publication
from .researcher   import Researcher
from .state        import State
