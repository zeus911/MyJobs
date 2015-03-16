from datetime import datetime
import json

from django.core import serializers
from django.core.files.base import ContentFile
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models.loading import get_model
from django.db.models import Count
from django.http import HttpResponse, Http404
from django.shortcuts import render_to_response
from django.template import RequestContext

from myreports.decorators import restrict_to_staff
from myreports.helpers import serialize, parse_params, humanize
from myreports.models import Report
from universal.helpers import get_company_or_404
from universal.decorators import company_has_access

# TODO:
# * write unit tests for new report generation stuff
# * update documentation for views
# * look at class-based views
# * see about re-merging create_report and filter_records on get/post


@restrict_to_staff()
def reports(request):
    """The Reports app landing page."""
    company = get_company_or_404(request)

    success = 'success' in request.POST

    reports = Report.objects.filter(owner=company).order_by("-created_on")

    ctx = {
        "company": company,
        "success": success,
        "past_reports": reports
    }

    return render_to_response('myreports/reports.html', ctx,
                              RequestContext(request))


def get_states(request):
    if request.is_ajax():
        response = HttpResponse()
        html = render_to_response('includes/state_dropdown.html',
                                  {}, RequestContext(request))
        response.content = html.content
        return response
    else:
        raise Http404


def filter_records(request, model, params, ignore_cache=False):
    """
    View that returns a query set based on post data submitted with the
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
    name = params.pop('report_name', datetime.now())
    ignore_cache = params.pop('ignore_cache', False)
    records = filter_records(
        request, get_model(app, model), params, ignore_cache)

    contents = serialize('json', records)
    results = ContentFile(contents)
    report, created = Report.objects.get_or_create(
        name=name, created_by=user, owner=company, path=path,
        params=json.dumps(params.items()))

    report.results.save('%s-%s.json' % (name, report.pk), results)

    return HttpResponse()


def get_report(request):
    report_id = request.GET.get('report', 0)
    report = get_model('myreports', 'report').objects.get(pk=report_id)

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = "attachment; filename='%s-%s.csv'" % (
        report.name, report.pk)

    records = humanize(report.python)
    response = serialize('csv', records, output=response, as_is=True)

    return response
