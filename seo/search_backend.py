import operator

from haystack.backends import log_query, EmptyResults, SQ
from haystack.backends.solr_backend import SolrEngine, SolrSearchQuery
from haystack.backends.solr_backend import SolrSearchBackend
from haystack.constants import ID, DJANGO_CT
from haystack.query import SearchQuerySet
from haystack.utils import IDENTIFIER_REGEX
from django.conf import settings

from pysolr import SolrError
from seo_pysolr import Solr


class DESearchQuerySet(SearchQuerySet):
    #Tracks which parameters have been added with add_param
    search_parameters = []

    def narrow_exclude(self, query):
        clone = self._clone()
        clone.query.add_narrow_query("NOT (%s)" % query)
        return clone

    def facet_counts(self):
        return self.query.get_facet_counts()

    def add_facet_count(self, sqs2):
        """
        Returns sum of facet_counts from sqs2 and self.query

        Input:
        :sqs2: SearchQuerySet with facets to add to self facets 

        """
        if sqs2 is None:
            return self.facet_counts()

        facet_counts1 = self.facet_counts()
        facet_counts2 = sqs2.query.get_facet_counts()

        # field_counts = {facet_field: [(facet_field_value, count), ...], ...}
        field_counts1 = facet_counts1.get('fields')
        field_counts2 = facet_counts2.get('fields')

        for facet_field in field_counts2:
            # field_dict = {facet_field_value: count, ...}
            field_dict = dict(field_counts1[facet_field])

            for facet_field_value, count in field_counts2[facet_field]:
                current_count = field_dict.get(facet_field_value, 0)
                field_dict[facet_field_value] = current_count + count

            # Update the actual dictionary with the new results.
            field_counts1[facet_field] = field_dict.items()
            # Sort the list of field count tuples by count
            # (2nd value in each tuple)
            field_counts1[facet_field].sort(key=lambda tup: tup[1], reverse=True)

        facet_counts1['fields'] = field_counts1
        return facet_counts1

    def facet_mincount(self, mincount):
        """Sets mincount for facet result."""
        clone = self._clone()
        clone.query.set_facet_mincount(mincount)
        return clone
    
    def facet_limit(self, limit):
        """Sets limit for facet result."""
        clone = self._clone()
        clone.query.set_facet_limit(limit)
        return clone

    def facet_prefix(self, prefix):
        """Sets prefix for facet result."""
        clone = self._clone()
        clone.query.set_facet_prefix(prefix)
        return clone
        
    def facet_offset(self, offset):
        """Sets offset for facet result."""
        clone = self._clone()
        clone.query.set_facet_offset(offset)
        return clone
        
    def facet_sort(self, sort):
        """Sets sort for facet result."""
        clone = self._clone()
        clone.query.set_facet_sort(sort)
        return clone

    #TODO. Replace redundant methods with set_param.
    #Jason McLaughlin 09/27/2012
    def add_param(self, param, value):
        """
        Sets an arbitrary Solr parameter.

        Inputs:
        :param: solr parameter to set
        :value: value to assign to solr parameter

        """
        clone = self._clone()
        clone.query.set_param(param, value)
        self.search_parameters.append(param)
        return clone

    def bf(self, bf):
        """
        Sets Boost Functions for SearchQuerySet to use when building queries. 
        Compatable with Solr's Dismax and Extended Dismax query parsers

        Input:
        :bf: A string defining one or more Solr Functions used to boost
        relevancy score. For examples and a list of functions available
        see Solr docs

        """
        clone = self._clone()
        clone.query.set_bf(bf)
        return clone

    def fields(self, fields):
        """
        Method for specifying what fields to return from the search
        query. It is a wrapper for Solr's `fl` parameter:
        http://wiki.apache.org/solr/CommonQueryParameters#fl

        Input:
        :fields: An iterable of strings. Each element of `fields` must
        correlate to a field on the Solr schema.
        
        """
        # These fields must be included in every search because of Haystack
        # internals. If you remove this, Haystack will throw an exception.
        defaults = ['django_id', 'django_ct', 'score', 'id']
        clone = self._clone()
        clone.query.set_fields(fields+defaults)
        return clone
        
    def mfac(self, fields, fragment, **kwargs):
        """
        Multi-field checks for autocomplete.
        `fields` : Iterable composed of field names to search against
        `fragment`: The term sought
        
        """
        clone = self._clone()
        query_bits = []
        lookup = kwargs.get('lookup', '')

        for field in fields:
            subqueries = []
            for word in fragment.split(' '):
                kwargs = {field + lookup: word}
                subqueries.append(SQ(**kwargs))
            query_bits.append(reduce(operator.and_, subqueries))

        return clone.filter(reduce(operator.or_, query_bits))

    def query_facet(self, query):
        """
        Adds a custom facet.query.

        """
        clone = self._clone()
        clone.query.add_query_facet(query)
        return clone


class DESolrSearchQuery(SolrSearchQuery):
    search_parameters = []

    def __init__(self, using):
        super(SolrSearchQuery, self).__init__(using)
        self.facet_mincount = None
        self.facet_limit = None
        self.facet_prefix = None
        self.facet_sort = None
        self.facet_offset = None
        self.fields = None
        self.bf = None

    def build_params(self, *args, **kwargs):
        search_kwargs = super(DESolrSearchQuery, self).build_params(*args,
                                                                    **kwargs)
        """
        build_params logic was copied out into run(). dwithin, within, models, and
        distance_point were left out. I'm not sure if they were left out for a
        reason, but since we don't currenlty need them, I'm going to delete them
        for now.
        Jason McLaughlin 09/27/2012
        """
        kwargs_to_delete = ['dwithin', 'within', 'distance_point', 'models']
        for kwarg in kwargs_to_delete:
            if kwarg in search_kwargs:
                del search_kwargs[kwarg]

        attr_to_copy = ['facet_mincount', 'facet_limit', 'facet_prefix',
                        'facet_sort', 'facet_offset', 'bf']
        attr_to_copy.extend(self.search_parameters)

        #Copy attributes from Search query to search_kwargs
        for attr_name in attr_to_copy:
            attr = getattr(self, attr_name, False)
            if attr:
                search_kwargs[attr_name] = attr

        return search_kwargs

    def set_bf(self, bf):
        """
        Sets Boost Functions for SearchQuery use when building Solr queries. 
        Compatable with Solr's Dismax and Extended Dismax query parsers

        Input:
        :bf: A string defining one or more Solr Functions used to boost
        relevancy score. 

        """
        self.bf = bf

    #TODO Replace redundant set_foo methods with set_param
    def set_param(self, param, value):
        self.search_parameters.append(param)
        setattr(self, param, value)

    def set_facet_limit(self, limit):
        self.facet_limit = limit

    def set_facet_prefix(self, prefix):
        self.facet_prefix = prefix

    def set_facet_sort(self, sort):
        self.facet_sort = sort

    def set_facet_offset(self, offset):
        self.facet_offset = offset

    def set_facet_mincount(self, mincount):
        self.facet_mincount = mincount

    def set_fields(self, fieldlist):
        self.fields = fieldlist

    def _clone(self, *args, **kwargs):
        clone = super(SolrSearchQuery, self)._clone(*args, **kwargs)
        clone.facet_mincount = self.facet_mincount
        clone.facet_limit = self.facet_limit
        clone.facet_prefix = self.facet_prefix
        clone.facet_sort = self.facet_sort
        clone.facet_offset = self.facet_offset
        clone.fields = self.fields
        clone.bf = self.bf
        for param in self.search_parameters:
            setattr(clone, param, getattr(self, param, ""))

        return clone

    def add_query_facet(self, query):
        self.query_facets.append(query)


class DESolrSearchBackend(SolrSearchBackend):
    def __init__(self, connection_alias, **connection_options):
        """
        Inputs:
        :HTTP_AUTH_USERNAME: Username used for http authentication
        :HTTP_AUTH_PASSWORD: Password used for http authentication

        """
        super(DESolrSearchBackend, self).__init__(connection_alias,
                                                  **connection_options)
        user = connection_options.get("HTTP_AUTH_USERNAME")
        passwd = connection_options.get("HTTP_AUTH_PASSWORD")
        self.conn = Solr(connection_options['URL'], auth=(user, passwd),
                         timeout=self.timeout)

    @log_query
    def search(self, query_string, sort_by=None, start_offset=0, end_offset=None,
               fields='', highlight=False, facets=None, date_facets=None,
               query_facets=None, narrow_queries=None, spelling_query=None,
               within=None, dwithin=None, distance_point=None,
               limit_to_registered_models=None, result_class=None,
               facet_mincount=None, facet_limit=None, facet_prefix=None,
               facet_sort=None, facet_offset=None, bf=None, **kwargs):
        """
        Overrides both search() and build_search_kwargs().

        """
        if len(query_string) == 0:
            return {
                'results': [],
                'hits': 0,
            }
        kwargs = {
            'fl': '* score',
            'mlt': 'false'
        }

        if fields:
            if isinstance(fields, (list, set)):
                fields = " ".join(fields)
            kwargs['fl'] = fields

       # This code was causing sort_by to break, but we're keeping it as a
       # reference in case we want to enable geographic sorting in the future.
       # Haystack does have an order_by_distance function, so this code might
       # not be necessary
       # Jason McLaughlin 10/30/2012
       # geo_sort = False
       # if sort_by is not None:
       #     if sort_by in ['distance asc', 'distance desc'] and distance_point:
       #         # Do the geo-enabled sort.
       #         lng, lat = distance_point['point'].get_coords()
       #         kwargs['sfield'] = distance_point['field']
       #         kwargs['pt'] = '%s,%s' % (lat, lng)
       #         geo_sort = True
       #
       #         if sort_by == 'distance asc':
       #             kwargs['sort'] = 'geodist() asc'
       #         else:
       #             kwargs['sort'] = 'geodist() desc'
       #     else:
       #         if sort_by.startswith('distance '):
       #              warnings.warn("In order to sort by distance, "
       #                            "you must call the '.distance(...)' "
       #                            "method.")

        if sort_by is not None:
            # Regular sorting.
            kwargs['sort'] = sort_by

        if bf is not None:
            kwargs['bf'] = bf

        if start_offset is not None:
            kwargs['start'] = start_offset

        if end_offset is not None:
            kwargs['rows'] = end_offset - start_offset

        if highlight is True:
            kwargs['hl'] = 'true'
            kwargs['hl.fragsize'] = '100'
            kwargs['hl.snippets'] = '2'
            kwargs['hl.mergeContiguous'] = 'true'
            kwargs['hl.simple.pre'] = '<b>'
            kwargs['hl.simple.post'] = '</b>'

        if self.include_spelling is True:
            kwargs['spellcheck'] = 'true'
            kwargs['spellcheck.collate'] = 'true'
            kwargs['spellcheck.count'] = 1

            if spelling_query:
                kwargs['spellcheck.q'] = spelling_query

        if facets is not None:
            kwargs['facet'] = 'on'
            kwargs['facet.field'] = facets.keys()

            for facet_field, options in facets.items():
                for key, value in options.items():
                    kwargs['f.%s.facet.%s' % (facet_field, key)] = self.conn._from_python(value)

        if facet_mincount is not None:
            kwargs['facet'] = 'on'
            kwargs['facet.mincount'] = facet_mincount

        if facet_limit is not None:
            kwargs['facet'] = 'on'
            kwargs['facet.limit'] = facet_limit

        if facet_prefix is not None:
            kwargs['facet'] = 'on'
            kwargs['facet.prefix'] = facet_prefix

        if facet_sort is not None:
            kwargs['facet'] = 'on'
            kwargs['facet.sort'] = facet_sort

        if facet_offset is not None:
            kwargs['facet'] = 'on'
            kwargs['facet.offset'] = facet_offset

        if date_facets is not None:
            kwargs['facet'] = 'on'
            kwargs['facet.date'] = date_facets.keys()
            kwargs['facet.date.other'] = 'none'

            for key, value in date_facets.items():
                kwargs["f.%s.facet.date.start" % key] = self.conn._from_python(value.get('start_date'))
                kwargs["f.%s.facet.date.end" % key] = self.conn._from_python(value.get('end_date'))
                gap_by_string = value.get('gap_by').upper()
                gap_string = "%d%s" % (value.get('gap_amount'), gap_by_string)

                if value.get('gap_amount') != 1:
                    gap_string += "S"

                kwargs["f.%s.facet.date.gap" % key] = '+%s/%s' % (gap_string, gap_by_string)

        if query_facets is not None:
            kwargs['facet'] = 'on'
            kwargs['facet.query'] = query_facets

        if limit_to_registered_models is None:
            limit_to_registered_models = getattr(settings, 'HAYSTACK_LIMIT_TO_REGISTERED_MODELS', True)

        if limit_to_registered_models:
            # Using narrow queries, limit the results to only models handled
            # with the current routers.
            if narrow_queries is None:
                narrow_queries = set()

            registered_models = self.build_models_list()

            if len(registered_models) > 0:
                narrow_queries.add('%s:(%s)' % (DJANGO_CT, ' OR '.join(registered_models)))

        if narrow_queries is not None:
            kwargs['fq'] = list(narrow_queries)

        # if within is not None:
        #     from haystack.utils.geo import generate_bounding_box
        #
        #     kwargs.setdefault('fq', [])
        #     ((min_lat, min_lng), (max_lat, max_lng)) = generate_bounding_box(within['point_1'], within['point_2'])
        #     # Bounding boxes are min, min TO max, max. Solr's wiki was *NOT*
        #     # very clear on this.
        #     bbox = '%s:[%s,%s TO %s,%s]' % (within['field'], min_lat, min_lng, max_lat, max_lng)
        #     kwargs['fq'].append(bbox)

        # if dwithin is not None:
        #     kwargs.setdefault('fq', [])
        #     lng, lat = dwithin['point'].get_coords()
        #     geofilt = '{!geofilt pt=%s,%s sfield=%s d=%s}' % (lat, lng, dwithin['field'], dwithin['distance'].km)
        #     kwargs['fq'].append(geofilt)

        # # Check to see if the backend should try to include distances
        # # (Solr 4.X+) in the results.
        # if self.distance_available and distance_point:
        #     # In early testing, you can't just hand Solr 4.X a proper bounding box
        #     # & request distances. To enable native distance would take calculating
        #     # a center point & a radius off the user-provided box, which kinda
        #     # sucks. We'll avoid it for now, since Solr 4.x's release will be some
        #     # time yet.
        #     # kwargs['fl'] += ' _dist_:geodist()'
        #     pass

        try:
            raw_results = self.conn.search(query_string, **kwargs)
        except (IOError, SolrError), e:
            if not self.silently_fail:
                raise

            self.log.error("Failed to query Solr using '%s': %s", query_string, e)
            raw_results = EmptyResults()

        return self._process_results(raw_results, highlight=highlight,
                                     result_class=result_class)

    def build_schema(self, fields):
        content_field_name = ''
        schema_fields = []
            
        for field_name, field_class in fields.items():
            field_data = {
                'field_name': field_class.index_fieldname,
                'type': 'text_en',
                'indexed': 'true',
                'stored': 'true',
                'multi_valued': 'false',
            }

            if field_class.document is True:
                content_field_name = field_class.index_fieldname

            # DRL_FIXME: Perhaps move to something where, if none of these
            #            checks succeed, call a custom method on the form that
            #            returns, per-backend, the right type of storage?
            field_mapper = {'datetime': 'date',
                            'integer': 'long',
                            'string': 'text_en'}
            if field_class.field_type:
                field_data['type'] = field_mapper.get(field_class.field_type,
                                                      field_class.field_type)

            if field_class.is_multivalued:
                field_data['multi_valued'] = 'true'

            if field_class.stored is False:
                field_data['stored'] = 'false'

            # Do this last to override `text` fields.
            if field_class.indexed is False:
                field_data['indexed'] = 'false'

                # If it's text and not being indexed, we probably don't want
                # to do the normal lowercase/tokenize/stemming/etc. dance.
                if field_data['type'] == 'text_en':
                    field_data['type'] = 'string'

            # If it's a ``FacetField``, make sure we don't postprocess it.
            if hasattr(field_class, 'facet_for'):
                # If it's text, it ought to be a string.
                if field_data['type'] == 'text_en':
                    field_data['type'] = 'string'

                if fields[getattr(field_class, 'facet_for')].stored is False \
                        or fields[getattr(field_class,
                                          'facet_for')].stored == 'false':
                    field_data['stored'] = 'false'
                else:
                    field_data['stored'] = 'true'

            schema_fields.append(field_data)

        return (content_field_name, schema_fields)

    def remove(self, obj_or_string, commit=True):
        solr_id = get_identifier(obj_or_string)

        try:
            kwargs = {
                'commit': commit,
                ID: solr_id
            }
            self.conn.delete(**kwargs)
        except (IOError, SolrError), e:
            if not self.silently_fail:
                raise

            self.log.error("Failed to remove document '%s' from Solr: %s",
                           solr_id, e)

        
class DESolrEngine(SolrEngine):
    backend = DESolrSearchBackend
    query = DESolrSearchQuery


def get_identifier(obj_or_string):
    """
    Get an unique identifier for the object or a string representing the
    object.
    
    If not overridden, uses <app_label>.<object_name>.<pk>.
    """
    if isinstance(obj_or_string, basestring):
        if not IDENTIFIER_REGEX.match(obj_or_string):
            raise AttributeError("Provided string '%s' is not a "
                                 "valid identifier." % obj_or_string)
        
        return obj_or_string
    
    return u"%s.%s.%s" % (obj_or_string._meta.app_label,
                          obj_or_string._meta.module_name,
                          obj_or_string.uid)

