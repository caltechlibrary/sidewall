'''
publication.py: representation of a publication record

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
from .exceptions import *

class Publication(DimensionsCore):

    def _update_attributes(self, pub):
        super()._update_attributes(data)

        # https://docs.dimensions.ai/dsl/data.html#data
        self.altmetric               = pub.get('altmetric', '')
        self.book_doi                = pub.get('book_doi', '')
        self.book_series_title       = pub.get('book_series_title', '')
        self.book_title              = pub.get('book_title', '')
        self.date                    = pub.get('date', '')
        self.date_inserted           = pub.get('date_inserted', '')
        self.doi                     = pub.get('doi', '')
        self.field_citation_ratio    = pub.get('field_citation_ratio', '')
        self.id                      = pub.get('id', '')
        self.issn                    = pub.get('issn', '')
        self.issue                   = pub.get('issue', '')
        self.linkout                 = pub.get('linkout', '')
        self.journal                 = pub.get('journal', '')
        self.open_access             = pub.get('open_access', '')
        self.pages                   = pub.get('pages', '')
        self.pmcid                   = pub.get('pmcid', '')
        self.pmid                    = pub.get('pmid', '')
        self.proceedings_title       = pub.get('proceedings_title', '')
        self.publisher               = pub.get('publisher', '')
        self.references              = pub.get('references', '')
        self.relative_citation_ratio = pub.get('relative_citation_ratio', '')
        self.times_cited             = pub.get('times_cited', '')
        self.title                   = pub.get('title', '')
        self.type                    = pub.get('type', '')
        self.volume                  = pub.get('volume', '')
        self.year                    = pub.get('year', '')

        self.author_affiliations = []
        if 'author_affiliations' in pub:
            # All cases I've seen so far have been a list containing 1 list.
            if len(pub['author_affiliations']) > 1:
                raise DataMismatch('Affiliations list holds more than one list')

            for a in pub['author_affiliations'][0]:
                self.author_affiliations.append(Author(a))


        # FIXME still to do:
        #
        # journal_lists
        # supporting_grant_ids
        # recent_citations
        # FOR
        # funders
        # funder_countries
        # references
        # research_org_cities
        # research_org_countries
        # research_org_country_names
        # research_org_state_codes
        # research_org_state_names
        # research_orgs
        # researchers


    def __repr__(self):
        return "<Publication 0x{0:x}>".format(id(self))
