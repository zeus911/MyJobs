import json

from django.core import serializers
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models.loading import get_model
from django.db.models import Count
from django.http import HttpResponse, Http404
from django.shortcuts import render_to_response
from django.template import RequestContext

from myreports.decorators import restrict_to_staff
from myreports.models import Report
from universal.helpers import get_company_or_404
from universal.decorators import company_has_access


@restrict_to_staff()
def reports(request):
    """The Reports app landing page."""
    if request.is_ajax():
        response = HttpResponse()
        template = '{path}.html'
        html = render_to_response(template.format(path=request.POST['output']),
                                  {}, RequestContext(request))
        response.content = html.content
        return response

    return render_to_response('myreports/reports.html', {},
                              RequestContext(request))


def parse_params(querydict):
    params = {}
    for key in querydict.keys():
        value = querydict.get(key)
        value_list = querydict.getlist(key)

        # parsing a list parameter as a regular parameter only captures the
        # last item, so if trying both ways returns the same value, we can
        # be sure that it's not a list
        if value:
            if value == value_list[0]:
                params[key] = value
            else:
                # lists are not hashable
                params[key] = tuple(value_list)

    return params


# TODO: add doc for new calls
def filter_records(request, model, params, ignore_cache=False):
    """
    AJAX view that returns a query set based on post data submitted with the
    request, caching results by default.

    Inputs:
        :model: The model that should be filtered on.

    Output:
        A `QueryDict` filtered using params extracted from the request.

    Query Parameters:
        :start_date: Lower bound for record date-related field (eg. `datetime`
                     for `ContactRecord`).
        :end_date: Upper bound for record date-related field (eg. `datetime`
                   for `ContactRecord`).
        :ignore_cache: If present, this view's cache is ignored.

        Remaining query parameters are assumed to be field names of the model.

    Examples:
        The following should return all Contacts who are tagged as 'veteran':

            client.post(reverse('filter_records', kwargs={'model': 'contact'}),
                        tag=['veteran'])
    """
    company = get_company_or_404(request)
    user = request.user
    path = request.get_full_path()

    # get rid of empty params and flatten single-item lists

    cache_key = (user, company, path, tuple(params.items()))
    filter_records.cached = cache_key in filter_records.cache
    # fetch results from cache if available
    if not ignore_cache and filter_records.cached:
        records = filter_records.cache[cache_key]
    else:
        records = model.objects.from_search(company, params)
        filter_records.cache[cache_key] = records

    return records
filter_records.cache = {}


# render records?
def view_records(request, app, model, output='json'):
    if request.is_ajax() and request.method == 'POST':
        # parse request into dict, converting singleton lists into single items
        params = parse_params(request.POST)

        # remove non-query related params
        params.pop('csrfmiddlewaretoken', None)
        ignore_cache = params.pop('ignore_cache', False)
        count = params.pop('count', None)
        output = output or params.pop('output', 'json')

        records = filter_records(
            request, get_model(app, model), params, ignore_cache)

        counts = {}
        if count:
            records = records.annotate(count=Count(count))
            counts = {record.pk: record.count for record in records}

        if output == 'json':
            ctx = [dict({'pk': record['pk']}, **record['fields'])
                   for record in serializers.serialize('python', records)]
            if counts:
                ctx = [dict({'count': counts[record['pk']]}, **record)
                       for record in ctx]

            ctx = json.dumps(ctx, cls=DjangoJSONEncoder)
            response = HttpResponse(
                ctx, content_type='application/json; charset=utf-8')

        return response

    else:
        raise Http404("This view is only reachable via an AJAX POST request.")


@company_has_access('prm_access')
def create_report(request, app, model):
    company = get_company_or_404(request)
    user = request.user
    path = request.get_full_path()
    params = parse_params(request.POST)

    params.pop('csrfmiddlewaretoken', None)
    ignore_cache = params.pop('ignore_cache', False)
    records = filter_records(
        request, get_model(app, model), params, ignore_cache)

    # TODO: S3 storage
    Report.objects.get_or_create(
        created_by=user, owner=company, path=path,
        params=json.dumps(params.items()), results=records)
