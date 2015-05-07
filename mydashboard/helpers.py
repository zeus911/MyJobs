from collections import Counter
import urllib
from copy import copy
from datetime import datetime, timedelta
from urlparse import urlparse, urlunparse, parse_qsl

from django.conf import settings
from django.core import mail
from django.http import Http404

from universal.helpers import get_domain
from seo.models import SeoSite
from myprofile.models import EDUCATION_LEVEL_CHOICES
from solr.helpers import format_date, Solr
from countries import COUNTRIES
from universal.helpers import update_url_param

edu_codes = dict([(x, y) for x, y in EDUCATION_LEVEL_CHOICES])
country_codes = dict((x, y) for x, y in COUNTRIES)


def get_company_microsites(company):
    """
    Retrieves a given company's microsites

    Inputs:
    :company: Company whose microsites are being retrieved

    Outputs:
    :microsites: List of microsites
    :buids: List of buids associated with the company's microsites
    """
    job_source_ids = company.job_source_ids.all()
    buids = job_source_ids.values_list('id', flat=True)
    microsites = SeoSite.objects.filter(business_units__in=buids) \
        .values_list('domain', flat=True)
    return microsites, buids


def analytics(employer, company, candidate):
    if employer not in company.admins.all():
        raise Http404

    if hasattr(mail, 'outbox'):
        solr = settings.TEST_SOLR_INSTANCE
    else:
        solr = settings.SOLR

    analytics_solr = Solr(solr['current']).add_filter_query(
        'company_id:%d' % company.pk).add_query('User_id:%d' % candidate.pk)
    return analytics_solr.search().docs


def saved_searches(employer, company, candidate):
    """
    Function that gets employer's companies and those companies microsites.
    Will pull the domain out of the employer_microsites. Gathers the
    candidate's saved search urls and then will pull those urls
    out. Lastly, check to see if employer domains match up with
    candidate domains and return a list of urls.

    inputs:
    :employer:  The employer that is looking at candidate's page
    :candidate: The job seeker that shows up in employer's activitiy feed

    outputs:
                A list of candidate urls.
    """
    if employer not in company.admins.all():
        raise Http404

    employer_microsites = get_company_microsites(company)[0]
    candidate_searches = candidate.savedsearch_set.values_list('feed', flat=True)
    # Switch all company's microsites and candidate's saved searches to just
    # the domain so they can be easily compared.
    employer_domains = [get_domain(url).lower() for url in employer_microsites]
    candidate_domains = [get_domain(url).lower() for url in candidate_searches]

    return [url for url in candidate_domains if url in employer_domains]


def get_analytics_counts(actions):
    page_types = [entry.get('page_category', '') for entry in actions]
    return Counter(page_types)


def filter_by_domain(domain, user_solr=None, facet_solr=None):
    """
    Applies solr filters to SavedSearch.url based on a domain.

    inputs:
    :domain: The domain to filter the SavedSearches on.
    :user_solr: A Solr instance used for retrieving SavedSearch documents
        from solr.
    :facet_solr: A Solr instance used for retrieving facets based on
        ProfileUnits data.

    outputs:
    user_solr and facet_solr filtered by the company.

    """
    user_solr = Solr() if not user_solr else user_solr
    facet_solr = Solr() if not facet_solr else facet_solr

    query = 'SavedSearch_feed:*%s*' % domain

    user_solr = user_solr.add_filter_query(query)
    facet_solr = facet_solr.add_filter_query(query)

    return user_solr, facet_solr


def filter_by_microsite(company, user_solr=None, facet_solr=None):
    """
    Applies solr filters based on company.

    inputs:
    :microsites: A list of the microsites to filter the SavedSearches on.
    :user_solr: A Solr instance used for retrieving SavedSearch documents
        from solr.
    :facet_solr: A Solr instance used for retrieving facets based on
        ProfileUnits data.

    outputs:
    user_solr and facet_solr filtered by the company.

    """

    user_solr = Solr() if not user_solr else user_solr
    facet_solr = Solr() if not facet_solr else facet_solr

    query = 'SavedSearch_company_id:%s' % company.pk

    user_solr = user_solr.add_filter_query(query)
    facet_solr = facet_solr.add_query(query)
    user_solr = user_solr.add_filter_query('User_opt_in_employers:true')
    facet_solr = facet_solr.add_query('User_opt_in_employers:true')

    return user_solr, facet_solr


def filter_by_date(request, field=None):
    """
    Applies date filtering.

    inputs:
    :request: A. request object including fields from the date_range form
        in mydashboard.html.

    outputs:
    The start and end dates for the search, and the number of days the
    search covers.

    """
    requested_after_date = request.REQUEST.get('date_start', False)
    requested_before_date = request.REQUEST.get('date_end', False)
    if field is None:
        field = 'SavedSearch_created_on'

    date_end = datetime.now()
    # Set date range based on buttons
    if 'today' in request.REQUEST:
        date_range = filter_by_time_period(field,
                                           total_days=1)
        date_start = date_end - timedelta(days=1)
    elif 'seven_days' in request.REQUEST:
        date_range = filter_by_time_period(field,
                                           total_days=7)
        date_start = date_end - timedelta(days=7)
    elif 'thirty_days' in request.REQUEST:
        date_range = filter_by_time_period(field,
                                           total_days=30)
        date_start = date_end - timedelta(days=30)
    # Set date range based on date selection fields.
    else:
        if requested_after_date:
            date_start = datetime.strptime(requested_after_date, '%m/%d/%Y')
        else:
            date_start = request.REQUEST.get('date_start')
            if date_start:
                date_start = datetime.strptime(date_start, '%m/%d/%Y')
            else:
                # Default range is 30 days.
                date_start = datetime.now() - timedelta(days=30)

        if requested_before_date:
            date_end = datetime.strptime(requested_before_date, '%m/%d/%Y')
        else:
            date_end = request.REQUEST.get('date_end')
            if date_end:
                date_end = datetime.strptime(date_end, '%m/%d/%Y')
            else:
                # Default start date is today.
                date_end = datetime.now()
        date_range = filter_by_date_range(field=field,
                                          date_start=format_date(date_start,
                                                                 time_format="00:00:00Z"),
                                          date_end=format_date(date_end))

    days_delta = (date_end - date_start).days

    return date_range, date_start, date_end, days_delta


def apply_facets_and_filters(request, user_solr=None, facet_solr=None):
    """
    Applies facets to solr based on filters currently applied and creates
    a dictionary of removable terms and the resulting url with the term removed.

    inputs:
    :user_solr: A Solr instance used for retrieving SavedSearch documents
        from solr.
    :facet_solr: A Solr instance used for retrieving facets based on
        ProfileUnits data.
    :loc_solr: A solr instance used for retrieving facets based on
        location slabs.

    outputs:
    user_solr, facet_solr, and loc_solr appropriately filtered as well as a
    dictionary of
    {'the applied filter': 'resulting url if the filter were removed'}
    """
    url = request.build_absolute_uri()
    date_start = request.REQUEST.get('date_start', None)
    date_end = request.REQUEST.get('date_end', None)
    if date_start:
        url = update_url_param(url, 'date_start',
                               request.REQUEST.get('date_start'))
    if date_end:
        url = update_url_param(url, 'date_end',
                               request.REQUEST.get('date_end'))

    filters = {}
    user_solr = Solr() if not user_solr else user_solr
    facet_solr = Solr() if not facet_solr else facet_solr

    # The location parameter should be "Country-Region-City". Faceting
    # is determined on what is already in the location parameter.
    # No location facets on country, country parameter facets on state, and
    # country-state facets on city.
    if not 'location' in request.GET:
        facet_solr = facet_solr.add_facet_field('Address_country_code')
        facet_solr = facet_solr.add_facet_field('Address_region')
    else:
        fieldname = 'Address_full_location'

        term = urllib.unquote(request.GET.get('location'))
        search_term = term.replace("-", "##").replace(" ", "\ ")
        if len(term.split("-")) == 3:
            q = '%s:%s' % (fieldname, search_term)
        else:
            q = '%s:%s##*' % (fieldname, search_term)
        user_solr = user_solr.add_query(q)
        facet_solr = facet_solr.add_filter_query(q)

        term_list = term.split("-")
        term_len = len(term_list)

        prefix = '%s##' % term.replace('-', '##')
        if term_len == 3:
            # Country, Region, City included. No reason to facet on location.
            city = term_list[2] if term_list[2] else 'None'
            region = term_list[1] if term_list[1] else 'None'
            country = term_list[0]
            remove_term = "%s, %s, %s" % (city, region, country)
            new_val = "%s-%s" % (term_list[0], term_list[1])
            filters[remove_term] = update_url_param(url, 'location', new_val)
        elif term_len == 2:
            # Country, Region included.
            region = term_list[1] if term_list[1] else 'None'
            country = term_list[0]
            remove_term = "%s, %s" % (region, country)
            filters[remove_term] = update_url_param(url, 'location', term_list[0])
            facet_solr = facet_solr.add_facet_field(fieldname)
            facet_solr = facet_solr.add_facet_prefix(prefix, fieldname=fieldname)
        elif term_len == 1:
            # Country included.
            country = country_codes.get(term_list[0], term_list[0])
            filters[country] = remove_param_from_url(url, 'location')
            facet_solr = facet_solr.add_facet_field('Address_region')
            facet_solr = facet_solr.add_facet_prefix(prefix, fieldname=fieldname)

    if not 'education' in request.GET:
        facet_solr = facet_solr.add_facet_field('Education_education_level_code')
    else:
        term = urllib.unquote(request.GET.get('education'))
        term_name = edu_codes.get(int(term))
        filters[term_name] = remove_param_from_url(url, 'education')

        q = 'Education_education_level_code:%s' % term
        user_solr = user_solr.add_query(q)
        facet_solr = facet_solr.add_filter_query(q)

    if not 'license' in request.GET:
        facet_solr = facet_solr.add_facet_field('License_license_name')
    else:
        term = urllib.unquote(request.GET.get('license'))
        filters[term] = remove_param_from_url(url, 'license')

        q = 'License_license_name:"%s"' % term
        user_solr = user_solr.add_query(q)
        facet_solr = facet_solr.add_filter_query(q)

    return user_solr, facet_solr, filters


def remove_param_from_url(url, param):
    """
    Removes a specified field from a query string

    inputs:
    :url: The url containing the query string to be updated.
    :param: The param to be removed from the url.

    outputs:
    The new url.

    """
    url_parts = list(urlparse(url))
    parts = copy(url_parts)
    query = dict(parse_qsl(parts[4]))
    try:
        del query[param]
    except KeyError:
        return url
    parts[4] = urllib.urlencode(query)
    return urlunparse(parts)


def parse_facets(solr_results, request, add_unmapped_fields=False):
    """
    Turns solr facet results into dictionary of tuples that is compatible
    with the filter widget.

    e.g. output:
    {'filter_name': [('term': facet_count), ...],
     'Country': [('USA': 100), ('CHN": 50), ...]}

    """
    facet_mapping = {
        'License_license_name': 'License',
        'Address_country_code': 'Country',
        'Address_region': 'Region',
        'Address_full_location': 'City',
        'Education_education_level_code': 'Education',
    }

    facets = {}
    facet_fields = solr_results.facets.get('facet_fields', None)
    facet_queries = solr_results.facets.get('facet_queries', None)
    if facet_fields and facet_queries:
        solr_facets = dict(facet_fields.items() + facet_queries.items())
    elif facet_fields:
        solr_facets = facet_fields
    elif facet_queries:
        solr_facets = facet_queries
    else:
        return {}

    for solr_val, facet_val in facet_mapping.items():
        if solr_val in solr_facets:
            l = solr_facets.get(solr_val, None)
            if l:
                facets[facet_val] = get_urls(sorted(zip(l[::2], l[1::2]),
                                             key=lambda x: x[1], reverse=True),
                                             facet_val,
                                             request)
                if facet_val == 'Country':
                    facets[facet_val] = update_country(facets[facet_val])
                if facet_val == 'Region' or facet_val == 'City':
                    facets[facet_val] = update_location(facets[facet_val])
                if facet_val == 'Education':
                    facets[facet_val] = update_education_codes(facets[facet_val])
                del solr_facets[solr_val]

    if add_unmapped_fields:
        facets.update(solr_facets)

    return facets


def update_country(facet_tups):
    """
    Updates the education level displayed from the level code to the string
    matching that code.

    """
    facets = []
    for tup in facet_tups:
        new_tup = (country_codes.get(tup[0], 'None'), tup[1], tup[2])
        facets.append(new_tup)
    return facets


def update_location(facet_tups):
    """
    Updates the displayed location being searched on to be human readable.

    """
    facets = []
    for tup in facet_tups:
        location = [x if x else "None" for x in reversed(tup[0].split("##"))]
        location = ", ".join(location)
        location = location if location else 'None'
        new_tup = (location, tup[1], tup[2])
        facets.append(new_tup)
    return facets


def update_education_codes(facet_tups):
    """
    Updates the education level displayed from the level code to the string
    matching that code.

    """
    facets = []
    for tup in facet_tups:
        new_tup = (edu_codes.get(int(tup[0]), 'None'), tup[1], tup[2])
        facets.append(new_tup)
    return facets


def get_urls(facet_tups, param, request):
    """
    Creates urls for facets of search with facet applied as a filter..

    """
    url = request.build_absolute_uri()
    date_start = request.REQUEST.get('date_start', None)
    date_end = request.REQUEST.get('date_end', None)
    if date_start:
        url = update_url_param(url, 'date_start',
                               request.REQUEST.get('date_start'))
    if date_end:
        url = update_url_param(url, 'date_end',
                               request.REQUEST.get('date_end'))

    facets = []

    if param in ['Country', 'Region', 'City']:
        param = 'location'

    for tup in facet_tups:
        url_parts = list(urlparse(url))
        query = dict(parse_qsl(url_parts[4]))
        term = urllib.quote(tup[0].encode('utf8'))
        if param == 'location' and 'location' in query:

            query['location'] = "%s-%s" % (query['location'],
                                           tup[0].split("##")[-1])
        else:
            params = {param.lower(): term}
            query.update(params)
        url_parts[4] = urllib.urlencode(query)
        facets.append(tup + (urlunparse(url_parts), ))

    return facets


def filter_by_time_period(field, date_end=datetime.now(),
                          total_days=1):
    """
    Creates a string for a solr search of a date range spanning one or more
    days, ending on date_end.

    inputs:
    :field: The field that contains the time period being filtered on.
    :date_end: The latest date included in the search.
    :total_days: The total number of days the search should span.

    """
    query = "{field}:[{date_end}-{total_days}DAYS TO {date_end}]"
    time_filter = query.format(field=field, total_days=total_days,
                               date_end=format_date(date_end))
    return time_filter


def filter_by_date_range(field, date_start=datetime.now()-timedelta(days=1),
                         date_end=datetime.now()):
    """
    Creates a string for a solr search of a date range of date_start
    to date_end.

    inputs:
    :field: The field that contains the date range being filtered on.
    :date_end: The latest date included in the search.
    :total_days: The total number of days the search should span.

    """
    query = "{field}:[{date_start} TO {date_end}]"
    time_filter = query.format(field=field, date_start=date_start,
                               date_end=date_end)
    return time_filter
