'''
publication.py: representation of a publication record

This offers the various properties defined in the Dimensions documentation
for publication objects, with one modification: this object class introduces
a property named "authors" that is an alias for the "author_affiliations"
property that Dimensions uses.  The reason for creating a field name that
does not exist in Dimensions is that I found "author_affiliations" too
confusing (because it's not just the affiliations -- it's the actual author
list too) and, simultaneously, the lack of an "authors" field really
unintuitive for a publication.  Still, creating two ways of accessing the
same data is not ideal and may introduce code maintenance issues in the
future.  Time will tell.

Authors
-------

Michael Hucka <mhucka@caltech.edu> -- Caltech Library

Copyright
---------

Copyright (c) 2019 by the California Institute of Technology.  This code is
open-source software released under a 3-clause BSD license.  Please see the
file "LICENSE" for more information.

'''

from .author import Author
from .core import DimensionsCore
from .debug import log
from .exceptions import *
from .journal import Journal

class Publication(DimensionsCore):
    # Note: do NOT add "authors" to the following list.  The "authors" property
    # is something we add, and is not present in Dimensions.
    _attributes = ['altmetric', 'author_affiliations', 'book_doi',
                   'book_series_title', 'book_title', 'date', 'date_inserted',
                   'doi', 'field_citation_ratio', 'id', 'issn', 'issue',
                   'journal', 'linkout', 'mesh_terms', 'open_access', 'pages',
                   'pmcid', 'pmid', 'proceedings_title', 'publisher',
                   'references', 'relative_citation_ratio',
                   'research_org_country_names', 'research_org_state_names',
                   'supporting_grant_ids' 'times_cited', 'title', 'type',
                   'volume', 'year'] + DimensionsCore._attributes


    def _update_attributes(self, data):
        if __debug__: log('updating object {} using {}', id(self), data)
        if not isinstance(data, dict):
            raise InternalError('Data not in dict format')
        super()._update_attributes(data)

        objattr = lambda attr: object.__getattribute__(self, attr)
        set_objattr = lambda attr, value: object.__setattr__(self, attr, value)

        set_objattr('altmetric',                  data.get('altmetric', ''))
        set_objattr('book_doi',                   data.get('book_doi', ''))
        set_objattr('book_series_title',          data.get('book_series_title', ''))
        set_objattr('book_title',                 data.get('book_title', ''))
        set_objattr('date',                       data.get('date', ''))
        set_objattr('date_inserted',              data.get('date_inserted', ''))
        set_objattr('doi',                        data.get('doi', ''))
        set_objattr('field_citation_ratio',       data.get('field_citation_ratio', ''))
        set_objattr('id',                         data.get('id', ''))
        set_objattr('issn',                       data.get('issn', ''))
        set_objattr('issue',                      data.get('issue', ''))
        set_objattr('linkout',                    data.get('linkout', ''))
        set_objattr('mesh_terms',                 data.get('mesh_terms', ''))
        set_objattr('open_access',                data.get('open_access', ''))
        set_objattr('pages',                      data.get('pages', ''))
        set_objattr('pmcid',                      data.get('pmcid', ''))
        set_objattr('pmid',                       data.get('pmid', ''))
        set_objattr('proceedings_title',          data.get('proceedings_title', ''))
        set_objattr('publisher',                  data.get('publisher', ''))
        set_objattr('references',                 data.get('references', ''))
        set_objattr('relative_citation_ratio',    data.get('relative_citation_ratio', ''))
        set_objattr('research_org_country_names', data.get('research_org_country_names', ''))
        set_objattr('research_org_state_names',   data.get('research_org_state_names', ''))
        set_objattr('supporting_grant_ids',       data.get('supporting_grant_ids', ''))
        set_objattr('times_cited',                data.get('times_cited', ''))
        set_objattr('title',                      data.get('title', ''))
        set_objattr('type',                       data.get('type', ''))
        set_objattr('volume',                     data.get('volume', ''))
        set_objattr('year',                       data.get('year', ''))

        # Journal is an object.
        set_objattr('journal', Journal(data['journal'], self) if 'journal' in data else '')

        # Affiliations are a list.
        set_objattr('author_affiliations', [])
        if 'author_affiliations' in data:
            # All cases seen so far have been a list containing another list.
            # I don't understand the point of the double list. Let's be cautious.
            if len(data['author_affiliations']) > 1:
                raise DataMismatch('Affiliations list holds more than one list')
            for a in data['author_affiliations'][0]:
                self.author_affiliations.append(Author(a, self))


    @property
    def authors(self):
        '''Alias for the "author_affiliations" property on Publication.'''
        return self.author_affiliations


    @authors.setter
    def authors(self, alist):
        '''Alias for the "author_affiliations" property on Publication.'''
        self.author_affiliations = alist


    def __repr__(self):
        return "<Publication {}>".format(self.id)
