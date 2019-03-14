'''
grant.py: representation of a grant

Authors
-------

Michael Hucka <mhucka@caltech.edu> -- Caltech Library

Copyright
---------

Copyright (c) 2019 by the California Institute of Technology.  This code is
open-source software released under a 3-clause BSD license.  Please see the
file "LICENSE" for more information.
'''

from .category     import Category
from .city         import City
from .core         import DimensionsCore
from .country      import Country
from .data_helpers import objattr, set_objattr, new_object
from .debug        import log
from .exceptions   import DataMismatch
from .organization import Organization
from .researcher   import Researcher
from .state        import State


class Grant(DimensionsCore):
    _new_attributes = ['FOR', 'FOR_first', 'HRCS_HC', 'HRCS_RAC', 'RCDC',
                       'abstract', 'active_year', 'date_inserted', 'end_date',
                       'funder_countries', 'funders', 'funding_aud',
                       'funding_cad', 'funding_chf', 'funding_eur',
                       'funding_gbp', 'funding_jpy', 'funding_org_acronym',
                       'funding_org_city', 'funding_org_name', 'funding_usd',
                       'id', 'language', 'linkout', 'original_title',
                       'project_num', 'research_org_cities',
                       'research_org_countries', 'research_org_name',
                       'research_org_state_codes', 'research_orgs',
                       'researchers', 'start_date', 'start_year', 'title',
                       'title_language']
    _attributes     = _new_attributes + DimensionsCore._attributes


    def _set_attributes(self, data, overwrite = False):
        if __debug__: log('setting attributes on {} using {}', id(self), data)

        # Attributes that are plain strings or simple lists.
        set_objattr(self, 'abstract',            data.get('abstract', ''),            overwrite)
        set_objattr(self, 'active_year',         data.get('active_year', ''),         overwrite)
        set_objattr(self, 'date_inserted',       data.get('date_inserted', ''),       overwrite)
        set_objattr(self, 'end_date',            data.get('end_date', ''),            overwrite)
        set_objattr(self, 'funding_aud',         data.get('funding_aud', ''),         overwrite)
        set_objattr(self, 'funding_cad',         data.get('funding_cad', ''),         overwrite)
        set_objattr(self, 'funding_chf',         data.get('funding_chf', ''),         overwrite)
        set_objattr(self, 'funding_eur',         data.get('funding_eur', ''),         overwrite)
        set_objattr(self, 'funding_gbp',         data.get('funding_gbp', ''),         overwrite)
        set_objattr(self, 'funding_jpy',         data.get('funding_jpy', ''),         overwrite)
        set_objattr(self, 'funding_org_acronym', data.get('funding_org_acronym', ''), overwrite)
        set_objattr(self, 'funding_org_city',    data.get('funding_org_city', ''),    overwrite)
        set_objattr(self, 'funding_org_name',    data.get('funding_org_name', ''),    overwrite)
        set_objattr(self, 'funding_usd',         data.get('funding_usd', ''),         overwrite)
        set_objattr(self, 'id',                  data.get('id', ''),                  overwrite)
        set_objattr(self, 'language',            data.get('language', ''),            overwrite)
        set_objattr(self, 'linkout',             data.get('linkout', ''),             overwrite)
        set_objattr(self, 'original_title',      data.get('original_title', ''),      overwrite)
        set_objattr(self, 'project_num',         data.get('project_num', ''),         overwrite)
        set_objattr(self, 'research_org_name',   data.get('research_org_name', ''),   overwrite)
        set_objattr(self, 'start_date',          data.get('start_date', ''),          overwrite)
        set_objattr(self, 'start_year',          data.get('start_year', ''),          overwrite)
        set_objattr(self, 'title',               data.get('title', ''),               overwrite)
        set_objattr(self, 'title_language',      data.get('title_language', ''),      overwrite)

        # Remaining attributes are stored as objects, and we delay expanding
        # them until they're accessed.  See _lazy_expand().


    def _lazy_expand(self, data):
        # Be careful not to invoke "self.x" b/c it causes infinite recursion.
        super()._lazy_expand(data)
        if __debug__: log('expanding attributes on {} using {}', id(self), data)
        make_objects_list = objattr(self, '_make_objects_list')

        # All of these next ones become Category objects.
        make_objects_list('FOR',       Category, data)
        make_objects_list('FOR_first', Category, data)
        make_objects_list('HRCS_HC',   Category, data)
        make_objects_list('HRCS_RAC',  Category, data)
        make_objects_list('RCDC',      Category, data)

        # The following have various object types.
        make_objects_list('funder_countries',         Country, data)
        make_objects_list('funders',                  Organization, data)
        make_objects_list('research_org_cities',      City, data)
        make_objects_list('research_org_countries',   Country, data)
        make_objects_list('research_org_state_codes', State, data)

        # Special cases
        make_objects_list('researchers', Researcher, data)
        for details in data.get('researcher_details', []):
            for researcher in objattr(self, 'researchers'):
                if researcher.id != details['id']:
                    continue
                researcher._lazy_expand(details)
                researcher._set_affiliations(details, 'affiliations')

        # Bizarrely, the org data stored under the recipient researcher's
        # affiliations list is often more complete than the "research_orgs"
        # field, even though they are usually the same org.  So create objects
        # using the 'research_orgs' field, then update them with the data
        # in the researchers' affiliations list.
        make_objects_list('research_orgs', Organization, data)
        research_orgs = objattr(self, 'research_orgs')
        for researcher in data.get('researcher_details', []):
            for aff_org in researcher.get('affiliations', []):
                for res_org in research_orgs:
                    if res_org.id == aff_org['id']:
                        res_org._set_attributes(aff_org, overwrite = False)


    def _fill_record(self, data):
        # Be careful not to invoke "self.x" b/c it causes infinite recursion.
        if __debug__: log('filling object {} using {}', id(self), data)
        # Update any missing fields
        set_attributes = objattr(self, '_set_attributes')
        set_attributes(data, overwrite = False)


    def _make_objects_list(self, field, oclass, data, overwrite = True):
        cname = oclass.__name__
        if __debug__: log('creating {} objects for "{}" on {}', cname, field, id(self))
        if not data.get(field, None):
            if __debug__: log('field "{}" missing or empty {}', field, id(self))
            if overwrite:
                field_data = []
            else:
                return
        else:
            field_data = data[field]
        if not isinstance(field_data, list):
            obj_id = objattr(self, 'id')
            raise DataMismatch('Unexpected data received for "{}"'.format(obj_id))

        values = objattr(self, field, [])
        dimensions = objattr(self, '_dimensions')
        for item_data in field_data:
            obj = new_object(oclass, item_data, dimensions, self)
            # Do another round of setting attributes based on the 2nd set of
            # data that we purposefully pulled out above using the 'field' arg.
            set_attributes = objattr(obj, '_set_attributes')
            set_attributes(item_data, overwrite = False)
            values.append(obj)
        set_objattr(self, field, values, overwrite)
