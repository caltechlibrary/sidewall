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
from .data_helpers import objattr, set_objattr
from .debug import log
from .exceptions import *
from .journal import Journal


class Publication(DimensionsCore):
    # Note: do NOT add "authors" to the following list.  The "authors" property
    # is something we add, and is not present in Dimensions.
    _new_attributes = ['altmetric', 'author_affiliations', 'book_doi',
                       'book_series_title', 'book_title', 'date',
                       'date_inserted', 'doi', 'field_citation_ratio', 'id',
                       'issn', 'issue', 'journal', 'linkout', 'mesh_terms',
                       'open_access', 'pages', 'pmcid', 'pmid',
                       'proceedings_title', 'publisher', 'references',
                       'relative_citation_ratio', 'research_org_country_names',
                       'research_org_state_names', 'supporting_grant_ids',
                       'times_cited', 'title', 'type', 'volume', 'year']
    _attributes = _new_attributes + DimensionsCore._attributes


    def _set_attributes(self, data, overwrite = False):
        if __debug__: log('setting attributes on {} using {}', id(self), data)
        set_objattr(self, 'altmetric',                  data.get('altmetric', ''), overwrite)
        set_objattr(self, 'book_doi',                   data.get('book_doi', ''), overwrite)
        set_objattr(self, 'book_series_title',          data.get('book_series_title', ''), overwrite)
        set_objattr(self, 'book_title',                 data.get('book_title', ''), overwrite)
        set_objattr(self, 'date',                       data.get('date', ''), overwrite)
        set_objattr(self, 'date_inserted',              data.get('date_inserted', ''), overwrite)
        set_objattr(self, 'doi',                        data.get('doi', ''), overwrite)
        set_objattr(self, 'field_citation_ratio',       data.get('field_citation_ratio', ''), overwrite)
        set_objattr(self, 'id',                         data.get('id', ''), overwrite)
        set_objattr(self, 'issn',                       data.get('issn', ''), overwrite)
        set_objattr(self, 'issue',                      data.get('issue', ''), overwrite)
        set_objattr(self, 'linkout',                    data.get('linkout', ''), overwrite)
        set_objattr(self, 'mesh_terms',                 data.get('mesh_terms', ''), overwrite)
        set_objattr(self, 'open_access',                data.get('open_access', ''), overwrite)
        set_objattr(self, 'pages',                      data.get('pages', ''), overwrite)
        set_objattr(self, 'pmcid',                      data.get('pmcid', ''), overwrite)
        set_objattr(self, 'pmid',                       data.get('pmid', ''), overwrite)
        set_objattr(self, 'proceedings_title',          data.get('proceedings_title', ''), overwrite)
        set_objattr(self, 'publisher',                  data.get('publisher', ''), overwrite)
        set_objattr(self, 'references',                 data.get('references', ''), overwrite)
        set_objattr(self, 'relative_citation_ratio',    data.get('relative_citation_ratio', ''), overwrite)
        set_objattr(self, 'research_org_country_names', data.get('research_org_country_names', ''), overwrite)
        set_objattr(self, 'research_org_state_names',   data.get('research_org_state_names', ''), overwrite)
        set_objattr(self, 'supporting_grant_ids',       data.get('supporting_grant_ids', ''), overwrite)
        set_objattr(self, 'times_cited',                data.get('times_cited', ''), overwrite)
        set_objattr(self, 'title',                      data.get('title', ''), overwrite)
        set_objattr(self, 'type',                       data.get('type', ''), overwrite)
        set_objattr(self, 'volume',                     data.get('volume', ''), overwrite)
        set_objattr(self, 'year',                       data.get('year', ''), overwrite)

        # Journal is an object.
        j = Journal(data['journal'], self) if 'journal' in data else ''
        set_objattr(self, 'journal', j, overwrite)


    def _expand_attributes(self, data):
        if __debug__: log('expanding attributes on {} using {}', id(self), data)
        if 'author_affiliations' in data:
            try:
                affiliations = objattr(self, 'author_affiliations')
            except:
                affiliations = []
            # All cases seen so far have been a list containing another list.
            # I don't understand the point of the double list. Let's be cautious.
            if len(data['author_affiliations']) > 1:
                raise DataMismatch('Affiliations list holds more than one list')
            dimensions = objattr(self, '_dimensions')
            if dimensions:
                for a in data['author_affiliations'][0]:
                    affiliations.append(dimensions.factory(Author, a, self))
            else:
                for a in data['author_affiliations'][0]:
                    affiliations.append(Author(a, self))
            set_objattr(self, 'author_affiliations', affiliations, overwrite = True)


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
