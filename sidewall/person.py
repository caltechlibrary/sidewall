'''
person.py: base class for people records in Sidewall

Dimensions doesn't expose an underlying base class for people; instead, it
returns unnamed data structures that basically refer to people in different
contexts.  Sidewall currently understands two such contexts: authors of
publications (when a query uses 'return publications'), and "researchers"
(when a query uses 'return researchers' or objects such as 'Grant' contain
"researchers" as a data field).  Sidewall introduces a parent class called
'Person' because the objects in these two contexts are so similar, and
provides two derived classes: 'Author' and 'Researcher'.  Both of the derived
classes have the same fields.  The distinction provided by the derived
classes is necessary because the list of affiliations for an 'Author' is
relative to a particular publication and may not be all the affiliations that
a person has.  Thus, affiliations for authors must be understood in the
context of a particular search for publications.  The use of two classes
indicates the context, so that callers can correctly interpret the list of
affiliations.

           ┌──────────────┐
           │    Person    │
           └──────────────┘
                  ^
        ┌─────────┴──────────┐
┌───────┴──────┐      ┌──────┴───────┐
│    Author    │      │  Researcher  │
└──────────────┘      └──────────────┘

The 'affiliations' field in Sidewall's 'Person' (and consequently 'Author'
and 'Researcher') is a list of 'Organization' class objects.  Although
affiliations as returned by Dimensions are sparse when using a query that
ends with 'return researchers' (they consist only of organization
identifiers), Sidewall hides this by providing complete 'Organization'
objects for the 'affiliations' field of a 'Person', and using
behind-the-scenes queries to Dimensions to fill out the organization info
when the object field values are accessed.  Thus, calling programs do not
need to do anything to get organization details in a result regardless of
whether they use 'return publications' or 'return researchers' -- Sidewall
always provides 'Organization' class objects and handles getting the field
values automatically.

To make data access more uniform, Sidewall also replaces the field
'current_organization_id' (which in Dimensions is a string, the identifier of
an organization) with the field 'current_organization'.  Its value is an
'Organization' object corresponding to the organization whose identifier is
found in 'current_organization_id'.

Implementation notes
--------------------

This uses _fill_record() to update our object using a search template that
searches for a researcher by their Dimensions id.  The main reason for doing
this behind-the-scenes filling is the following.  It turns out that if you do
a search for publications in Dimensions and then grab the author info, you
will not necessarily get the same details about a given author for all of
that person's publications.  As best as I can tell from the circumstantial
evidence, the Dimensions system probably stores each publication as an
entirely separate document, with separate lists of authors for each one, and
does not always seek to reconcile differences in author information between
separate publications.  So, the same author (with the same Dimensions id) may
end up with a full name and an ORCID id in one publication record, but may
end up missing the ORCID in another publication record.  The consequence is
that the ORCID and other fields for a given person may be somewhere in their
system, but you can't be sure you'll get it in a particular publication
record.  So we have to do extra work to look for the missing fields.  To
complicate matters, given any publication result, there's no way to know
whether the author details are complete -- if something is missing (like the
ORCID), the only want to find out if Dimensions knows the value is to do
another search to look for it.

Limiting what we can do this way is another complication: the Dimensions
author records don't always contain a Dimensions id.  Without a unique id
to search for, we can't use the search approach to fill in missing fields.

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
from .data_helpers import objattr, set_objattr, dimensions_id, matching_record, new_object
from .debug import log
from .exceptions import *
from .organization import Organization


# A frustrating discovery has been that searching Dimensions with
#     search publications where researchers.id="{}" return researchers limit 1
# does NOT necessarily return the researcher that is identified by the id
# value in the argument.  (You would think that the first result would be the
# same researcher, but no.)  It turns out we have to iterate over multiple
# results and match the researcher id's to find the right record.
#
# So, that's the explanation for why the search template returns many results
# instead of a single one, and why _fill_record() iterates the way it does.

class Person(DimensionsCore):
    # The 'middle_name' field does not seem to show up in publication author
    # or researcher results, but does show up in researchers' lists on grants.
    _new_attributes = ['first_name', 'middle_name', 'last_name', 'id',
                       'orcid', 'current_organization']
    _attributes     = _new_attributes + DimensionsCore._attributes
    _search_tmpl    = 'publications where researchers.id="{}" return researchers'


    def _set_attributes(self, data, overwrite = False):
        if __debug__: log('setting attributes on {} using {}', id(self), data)
        set_objattr(self, 'first_name',  data.get('first_name', ''),  overwrite)
        set_objattr(self, 'middle_name', data.get('middle_name', ''), overwrite)
        set_objattr(self, 'last_name',   data.get('last_name', ''),   overwrite)
        set_objattr(self, 'id',          dimensions_id(data),         overwrite)

        # Dimensions uses a list for researcher's orcid in some cases but not
        # others.  Why?  Not clear if they ever associate more than one orcid
        # w someone.  Currently we assume there's never more than 1 orcid.
        orcid_value = data.get('orcid_id') or data.get('orcid') or ''
        set_objattr(self, 'orcid', _normalized_orcid(orcid_value), overwrite)


    # When _lazy_expand() gets called, it will be with a record for a
    # researcher, which looks like the example below. Note that the current
    # organization shows up in both current_organization_id and the list of
    # affiliations.  We fish out the data in the list of affiliations and hand
    # that to the creation of an Organization object for the current org field.
    #
    #    {'current_organization_id': 'grid.184769.5',
    #     'first_name': 'Arunima K.',
    #     'last_name': 'Singh',
    #     'orcid': "['0000-0002-7212-6310']",
    #     'researcher_id': 'ur.01137756010.32',
    #     'affiliations': [{'country': 'United States',
    #                       'state_code': 'US-CA',
    #                       'city': 'Berkeley',
    #                       'city_id': 5327684,
    #                       'id': 'grid.184769.5',
    #                       'country_code': 'US',
    #                       'state': 'California',
    #                       'name': 'Lawrence Berkeley National Laboratory'}]}

    def _lazy_expand(self, data):
        # Be careful not to invoke "self.x" b/c it causes infinite recursion.
        super()._lazy_expand(data)
        if __debug__: log('expanding attributes on {} using {}', id(self), data)
        org_from_data = objattr(self, '_org_from_data')
        set_objattr(self, 'current_organization', org_from_data(data))


    def _fill_record(self, data):
        # Be careful not to invoke "self.x" b/c it causes infinite recursion.
        if __debug__: log('filling object {} using {}', id(self), data)
        if not objattr(self, 'orcid') and 'orcid_id' in data:
            set_attributes = objattr(self, '_set_attributes')
            set_attributes(data, overwrite = True)
        if not objattr(self, 'current_organization', None):
            org_from_data = objattr(self, '_org_from_data')
            set_objattr(self, 'current_organization', org_from_data(data))


    def _org_from_data(self, data):
        org_id = data.get('current_organization_id', None)
        if org_id:
            org_record = {'id': org_id} # Fallback value.
            # If there's an affiliations list, one of them might contain
            # richer info about the organization. Let's try to find it.
            if 'affiliations' in data:
                org_record = matching_record(data, 'affiliations', org_id)
            dimensions = objattr(self, '_dimensions', None)
            return new_object(Organization, org_record, dimensions, self)
        else:
            return None


def _normalized_orcid(value):
    if isinstance(value, str) and '[' in value:
        # I suspect there's a bug in how I store test cases, but let's
        # handle the case where a list was turned into a string.
        return value.strip("'[]")
    elif isinstance(value, list):
        if len(value) > 1:
            raise DataMismatch('More than one ORCID id: {}'.format(value))
        return value[0]
    else:
        return value
