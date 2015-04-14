from collections import namedtuple
import datetime
import socket

from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from api.decorators import authorize_user, sns_json_message
from api.helpers import (get_cntl_query, get_rc_query,
                         get_query, get_query_as_string,
                         grouper)
from api.xmlparse import JobFeed
from tasks import task_update_solr


@csrf_exempt
@sns_json_message
def update(request):
    """
    Called when a job feed file is ready to be imported. Calls celery update
    tasks.

    """
    if request:
        if request.get('Subject', '') != 'END':
            buid = request.get('Subject', '')
            task_update_solr.delay(buid)


@authorize_user
def api(request, api_user, counts_api=False):
    status_code = 200
    jvid = request.GET.get('jvid')

    solr_search = get_query(request.GET, api_user)

    hits = 0
    if solr_search.results:
        start_row = int(solr_search.solr_parameters.get('start', 0)) + 1
        hits = solr_search.results.hits
        end_row = max(len(solr_search.results) + start_row - 1, 0)
        sort_order = solr_search.solr_parameters.get('sort', 'relevance')
        sort_order = ('initdate' if sort_order == 'date_new desc'
                      else 'relevance')
    else:
        start_row = 0
        end_row = 0
        sort_order = 'relevance'

    query = get_query_as_string(request.GET)

    data = {
        'is_counts': counts_api,
        'end_row': end_row,
        'error': solr_search.error or '',
        'jobs': solr_search.results.docs if solr_search.results else None,
        'query': query,
        'record_count': hits or 0,
        'search_id': solr_search.search.id if solr_search.search else 0,
        'search_time': datetime.datetime.now(),
        'server': socket.gethostname(),
        'sort_order': sort_order,
        'start_row': start_row,
        'user': api_user,
    }
    template = 'api.xml' if not jvid else 'job_view.xml'
    if solr_search.error:
        status_code = 400
    return render(request, template, data, content_type="application/xml",
                  status=status_code)


@authorize_user
def countsapi(request, api_user):
    status_code = 200
    params = request.REQUES
    cntl = params.get('cntl', 0)
    rc = params.get('rc', 0)
    param_onets = []

    company_facet = namedtuple('company_facet', ['name', 'buid', 'count'])
    location_facet = namedtuple('location_facet', ['location', 'count', ])
    onet_facet = namedtuple('onet_facet', ['code', 'count', ])

    # If cntl and rc flags aren't present, the results are almost identical
    # to the regular api, so let the regular api function handle it.
    if (not cntl or cntl == '0') and (not rc or rc == '0'):
        return api(request, counts_api=True)

    if cntl:
        template = 'cntl.xml'
        data = {
            'companies': None,
            'locations': None,
            'onets': None,
        }
        solr_search = get_cntl_query(request.GET, api_user)
    else:
        template = 'rc.xml'

        param_onets = params.get('onets', '').replace(" ", "").split(',')
        param_onets = param_onets + params.get('onet', '').split(',')
        param_onets = [JobFeed.clean_onet(onet) for onet in param_onets]

        data = {
            'onets': [(onet, 0) for onet in filter(None, param_onets)],
            'record_count': 0,
        }
        solr_search = get_rc_query(request.GET, api_user)

    if cntl and solr_search.results is not None:
        companies = []
        solr_facets = solr_search.results.facets['facet_fields']
        for c in grouper(solr_facets['company_slab_exact']):
            name, buid = c[0].split('::')
            companies.append(company_facet(name, buid, c[1]))
        locations = []
        for l in grouper(solr_facets['city_slab_exact']):
            location = l[0].replace('None, ', '')
            locations.append(location_facet(location, l[1]))
        onets = []
        for o in grouper(solr_facets['onet']):
            onets.append(onet_facet(o[0], o[1]))
        data = {
            'companies': sorted(companies, key=lambda x: x.count, reverse=True),
            'locations': sorted(locations, key=lambda x: x.count, reverse=True),
            'onets': sorted(onets, key=lambda x: x.count, reverse=True),
        }
    elif rc and solr_search.results is not None:
        solr_facets = solr_search.results.facets['facet_fields']
        solr_facets = dict(list(grouper(solr_facets['onet'])))

        onets = []
        for onet in filter(None, param_onets):
            count = solr_facets.get(onet, 0)
            onets.append(onet_facet(onet, count))

        data = {
            'onets': onets,
            'record_count': solr_search.results.hits,
        }

    if solr_search.error:
        status_code = 400
    return render(request, template, data, content_type="application/xml",
                  status=status_code)
