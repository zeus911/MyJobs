from copy import copy
from datetime import datetime
from itertools import izip_longest
import json
import pysolr

from django.conf import settings

from api.models import Search, Industry, Country
from api.models import CityToCentroidMapping as C2CM
from api.models import ZipCodeToCentroidMapping as ZC2CM
from moc_coding.models import Moc, Onet

# List of supported search parameters that have straight-foward
# translations into solr fq queries
simple_api_fields = ['onet', 'onets', 'tm', 'ind', 'cn', 'cname', 'i',
                     'moc', 'branch', 'location', 'ind', 'fc']

# Field mapping for {search parameter: solr field}
api_to_solr = {
    'onet': 'onet',
    'tm': 'date_new',
    'ind': 'ind',
    'cn': 'country',
    'cname': 'company',
    'i': 'staffing_code',
    'moc': 'moc',
    'rank': 'moc_slab',
    'branch': 'moc_slab',
    'location': 'all_locations',
    'fc': 'federal_contractor',
    'zc': 'all_locations',
}

# Field mapping for {search parameter: pysolr kwarg}
param_mapper = {
    'so': 'sort',
    'rs': 'start',
    're': 'rows',
}


class SolrSearch(object):
    def __init__(self):
        self.error = None
        self.query = ""
        self.results = None
        self.search = None
        self.solr_parameters = {
            # This function scales relevancy by date,
            # lowering the relevancy by up to 50% at 6 months.
            'bf': "recip(ms(NOW/HOUR,salted_date),1.8e-9,1,1)",
            'fq': [],
        }


def get_object_or_none(model, kwargs):
    try:
        return model.objects.get(**kwargs)
    except (model.DoesNotExist, model.MultipleObjectsReturned):
        return None


def get_attr_or_blank_string(model, kwargs, attr):
    obj = get_object_or_none(model, kwargs)
    if not obj:
        return ""

    return getattr(obj, attr, "")


def get_int_or_none(string):
    try:
        return int(string)
    except (ValueError, TypeError, UnicodeEncodeError):
        return None


def get_rc_query(query_dict, api_user):
    """
    A wrapper for get_query() that adds the facet.field parameter for
    countsapi rc searches.

    """
    solr_search = SolrSearch()
    solr_search.solr_parameters['facet'] = "true"
    solr_search.solr_parameters['facet.mincount'] = 1
    solr_search.solr_parameters['facet.limit'] = -1
    solr_search.solr_parameters['facet.field'] = ['onet']
    return get_query(query_dict, api_user, solr_search=solr_search)


def get_cntl_query(query_dict, api_user):
    """
    A wrapper for get_query() that adds the facet.field parameter for
    countsapi cntl searches.

    """
    solr_search = SolrSearch()
    solr_search.solr_parameters['facet'] = "true"
    solr_search.solr_parameters['facet.mincount'] = 1
    solr_search.solr_parameters['facet.limit'] = -1
    solr_search.solr_parameters['facet.field'] = ['company_buid_slab_exact',
                                                  'city_slab_exact',
                                                  'onet']
    return get_query(query_dict, api_user, solr_search=solr_search)


def get_query(query_dict, api_user, solr_search=None):
    """
    Inputs:
    :query_dict: A dictionary containing the search values
    :api_user: The APIUser that made the search
    :solr_search: Optional. A SolrSearch object to be added to.

    Outputs:
    A solr_search object with up-to-date error, query, results, search, and
        solr_parameters.

    """
    def _clean_onet(onet):
        onet = onet.replace('-', '').replace('.', '').replace(",", " OR ")
        # Onets like 37000000 should match 37101100, 37101200 and any other
        # onets starting with 37, so turn the 0s into a wildcard.
        onet = onet.replace('000000', '*')
        return onet

    def _clean_query(string):
        if not string:
            return ''
        string = string.replace("!=", "-")
        string = string.replace("|", " OR ").replace("&", " AND ")

        query_string = "text:({query})"
        return query_string.format(query=string)

    def _get_row(row):
        row = get_int_or_none(row)
        # Solr indexes from 0, but the api documentation suggests indexing
        # starts at 1.
        return row - 1 if row and row > 0 else 0

    query_dict = dict((k.encode('utf-8'), v.encode('utf-8')) for (k, v)
                      in query_dict.iteritems())

    if not solr_search:
        solr_search = SolrSearch()

    jvid = query_dict.get('jvid', '')[:32]
    if jvid and api_user.jv_api_access:
        solr_search.solr_parameters['fq'] = ['(guid:(%s))' % jvid]
        solr_search.query = '*:*'
        return get_solr_result(solr_search)
    elif jvid:
        solr_search.error = "Job No Longer Available"
        return solr_search

    search_id = query_dict.get('si')
    if search_id:
        try:
            search_id = get_int_or_none(search_id)
            solr_search.search = Search.objects.get(id=search_id, user=api_user)
            solr_search.solr_parameters.update(json.loads(solr_search.search.solr_params))
            solr_search.search.date_last_accessed = datetime.now()
            solr_search.search.save(update_fields=['date_last_accessed'])
        except Exception:
            solr_search.error = "Search matching id does not exist"
            return solr_search

    for param, value in query_dict.items():
        if param == 'so' and value:
            order = api_to_solr['tm'] if value == "initdate" else "score"
            value = "{order} desc".format(order=order)
        elif param == 'tm' and value:
            value = get_int_or_none(value)
            if value:
                value = "[NOW-{days}DAY TO NOW]".format(days=value)

        elif param in ['onet', 'onets'] and value:
            param = 'onet'
            value = _clean_onet(value)

        elif param == 'cn' and value:
            kwargs = {'country_code': value}
            value = get_attr_or_blank_string(Country, kwargs, 'country')
            value = '"{country}"'.format(country=value)

        elif param == 'i' and value:
            value = "True" if value == 's' else "False"

        elif param == 'ind' and value:
            kwargs = {'industry_id': value}
            value = get_attr_or_blank_string(Industry, kwargs, 'industry')
            value = '"{industry}"'.format(industry=value)

        elif param == 'rs' and value:
            value = _get_row(value)

        elif param == 're' and value:
            end = get_int_or_none(value) or 0
            end = max(end, 1)

            start = get_int_or_none(query_dict.get('rs', 1)) or 1
            start = max(start, 1)

            rows = min(500, end - start + 1)

            value = max(rows, 0)

        if param in simple_api_fields and value:
            fq = "{field}:({value})"
            fq = fq.format(field=api_to_solr[param], value=value)
            solr_search.solr_parameters['fq'].append(fq)
        elif param in param_mapper and value:
            solr_search.solr_parameters[param_mapper[param]] = value

    query = _clean_query(query_dict.get('kw'))
    # AND the search passed in through the kw param with any other fields
    # already added to the query.
    solr_search.query = " AND ".join(filter(None, [solr_search.query, query]))

    if solr_search.query:
        bq = solr_search.query.replace("text:", "title:")
        solr_search.solr_parameters['bq'] = bq

    # Include the query from the previous search if no new query
    # has been made.
    if solr_search.search and not solr_search.query:
        solr_search.query = solr_search.search.query

    req_loc = query_dict.get('zc') or query_dict.get('zc1')
    radius = query_dict.get('rd1', 25)
    if req_loc:
        solr_search = add_geolocation(req_loc, radius, solr_search)

    if not any([solr_search.query, solr_search.solr_parameters['fq']]):
        solr_search.error = "Search too broad"
        return solr_search
    elif not solr_search.query:
        solr_search.query = '*:*'

    if api_user.scope == '7':
        solr_search.solr_parameters['fq'].append('(network: (true))')

    params_str = json.dumps(solr_search.solr_parameters)
    if not solr_search.search:
        kwargs = {
            'query': solr_search.query,
            'solr_params': params_str,
            'user': api_user,
        }
        solr_search.search = Search.objects.create(**kwargs)
    return get_solr_result(solr_search)


def get_query_as_string(r):
    """
    Generates the human-readable query string for xml output.

    """
    onets = r.get('onets').split(",") if r.get('onets') else ''
    if not onets:
        onets = r.get('onet').split(",") if r.get('onet') else ''
    onets = [x.replace('-', '').replace('.', '') for x in onets]
    titles = []
    for x in onets:
        try:
            titles.append(Onet.objects.get(code__iexact=x).title)
        except (Onet.DoesNotExist, Onet.MultipleObjectsReturned):
            pass
    title_str = ", ".join([title for title in titles])

    # {search_field : [instance_name, query_field, model]}
    readable_fields = {'onet': ['', 'code', Onet],
                       'moc': ['', 'code__iexact', Moc],
                       'cn': ['', 'country_code', Country],
                       'ind': ['', 'industry_id', Industry]}

    for field in readable_fields:
        term = r.get(field)
        if term:
            kwargs = {readable_fields[field][1]: term}
            model = readable_fields[field][2]
            readable_fields[field][0] = get_object_or_none(model, kwargs)

    query = []
    if r.get('kw'):
        query.append("%s" % r.get('kw'))
    if title_str:
        query.append("%s" % title_str)
    if readable_fields['ind'][0]:
        query.append("in %s" % readable_fields['ind'][0].industry)
    if readable_fields['cn'][0]:
        query.append("in %s" % readable_fields['cn'][0])

    zc = r.get('zc')
    if zc:
        query.append("in %s" % zc)
    else:
        zc = r.get('zc1')
        rd = r.get('rd1', '25')
        if zc and ZC2CM.objects.filter(zip_code=zc).exists():
            query.append("in %s (within %s miles)" % (zc, rd))
        elif zc and ',' in zc:
            city = zc.split(",")[0].strip()
            state = zc.split(",")[1].strip()
            if C2CM.objects.filter(city=city, state=state).exists():
                query.append("in %s (within %s miles)" % (zc, rd))
            else:
                query.append("in %s" % zc)
        elif zc:
            query.append("in %s" % zc)

    if r.get('cname'):
        query.append("for %s" % r.get('cname'))

    if r.get('i'):
        query.append("posted by %s only" % ("Staffing Firms" if
                                            r.get('i') == "s" else "Employers"))
    if readable_fields['moc'][0]:
        query.append("matching occupation title %s" % readable_fields['moc'][0].title)
    if r.get('branch'):
        query.append("in %s" % r.get('branch'))
    if r.get('tm'):
        query.append("acquired in the last %s days" % r.get('tm'))

    return ' '.join(filter(None, query))


def add_geolocation(location, radius, solr_search):
    """
    Generates the solr formatting for geolocation search.

    """
    remove = ['"', "'", ' ']
    try:
        radius = int(radius)
    except ValueError:
        radius = 25
    lat = lon = ''

    if "," in location and radius > 0:
        # Should be a City, State pairing
        city = location.split(",")[0]
        state = location.split(",")[1]
        search_city = remove_strings(city, remove)
        search_state = remove_strings(state, remove)
        try:
            loc = C2CM.objects.get(city=search_city, state=search_state)
        except C2CM.DoesNotExist:
            pass
        else:
            lat = loc.centroid_lat
            lon = loc.centroid_lon
    elif radius > 0:
        search_zipcode = remove_strings(location, remove)[:5]
        try:
            # Check to see if valid zip code
            loc = ZC2CM.objects.get(zip_code=search_zipcode)
        except ZC2CM.DoesNotExist:
            pass
        else:
            lat = loc.centroid_lat
            lon = loc.centroid_lon

    if lat and lon:
        # miles -> km since geofilt only allows for km
        rd = int(radius) * 1.621371192
        query = "{!geofilt pt=%s,%s sfield=GeoLocation d=%s}" % (lat, lon, rd)
        solr_search.solr_parameters['fq'].append(query)
    else:
        # This means a matching city, state combo or zipcode couldn't be found
        # in our database, so we can't do a proper radius search.
        location_search = "(all_locations:({location}))".format(location=location)
        location_search = location_search.replace("OR", "\OR")
        solr_search.solr_parameters['fq'].append(location_search)

    return solr_search


def get_solr_result(solr_search):
    if solr_search.error:
        return solr_search

    try:
        solr = pysolr.Solr(settings.SOLR_LOCATION)
        solr_search.results = solr.search(q=solr_search.query,
                                          **solr_search.solr_parameters)
    except Exception, e:
        print e
        solr_search.error = "Query format error"

    return solr_search


def grouper(iterable):
    """
    Groups array elements into pairs, e.g. grouper('ABCDEFG') --> AB CD EF G

    """
    args = [iter(iterable)] * 2
    return izip_longest(fillvalue='', *args)


def remove_strings(replace_string, string_list):
    """
    Removes a list of strings from a string.

    :inputs:
        replace_string: The original string.
        string_list: A list of strings to be removed from replace_string

    :outputs:
        replace_string with all instances in string_list removed.

    """
    replace_string = copy(replace_string)
    for string in string_list:
        replace_string = replace_string.replace(string, '')
    return replace_string