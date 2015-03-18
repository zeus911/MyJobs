from datetime import datetime
import json

from django.core.files.base import ContentFile
from django.db.models.loading import get_model
from django.db.models import Count
from django.http import HttpResponse, Http404
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.utils.decorators import method_decorator
from django.views.generic import View

from myreports.decorators import restrict_to_staff
from myreports.helpers import filter_records, humanize, parse_params, serialize
from myreports.models import Report
from myreports.reports import PRMReport
from universal.helpers import get_company_or_404
from universal.decorators import company_has_access

# TODO:
# * write unit tests for new report generation stuff
# * update documentation for views


@restrict_to_staff()
def overview(request):
    """The Reports app landing page."""
    company = get_company_or_404(request)

    success = 'success' in request.POST

    reports = Report.objects.filter(owner=company).order_by("-created_on")
    report_count = reports.count()
    past_reports = reports[:10]

    ctx = {
        "company": company,
        "success": success,
        "past_reports": past_reports,
        "report_count": report_count
    }

    return render_to_response('myreports/reports.html', ctx,
                              RequestContext(request))


def report_archive(request):
    if request.is_ajax() and request.method == "POST":
        company = get_company_or_404(request)
        reports = Report.objects.filter(owner=company).order_by("-created_on")
        ctx = {
            "reports": reports
        }

        response = HttpResponse()
        html = render_to_response('myreports/report-archive.html', ctx,
                                  RequestContext(request))
        response.content = html.content

        return response


def get_states(request):
    if request.is_ajax():
        response = HttpResponse()
        html = render_to_response('includes/state_dropdown.html',
                                  {}, RequestContext(request))
        response.content = html.content
        return response
    else:
        raise Http404("This view is only reachable via an AJAX request")


def view_records(request, app, model, output='json'):
    if request.is_ajax():
        company = get_company_or_404(request)
        user = request.user

        # parse request into dict, converting singleton lists into single items
        params = parse_params(request.GET)

        # remove non-query related params
        params.pop('csrfmiddlewaretoken', None)
        ignore_cache = params.pop('ignore_cache', False)
        count = params.pop('count', None)
        output = output or params.pop('output', 'json')

        records = filter_records(
            company, user, app, model, params, ignore_cache)

        counts = {}
        if count:
            records = records.annotate(count=Count(count))
            counts = {record.pk: record.count for record in records}

        if output == 'json':
            ctx = serialize('json', records, counts=counts)
            response = HttpResponse(
                ctx, content_type='application/json; charset=utf-8')

        return response

    else:
        raise Http404("This view is only reachable via an AJAX POST request.")


def get_inputs(request):
    if request.is_ajax() and request.method == "GET":
        report_id = request.GET.get('id', 0)
        report = get_object_or_404(Report, pk=report_id)
        return HttpResponse(
            report.params, content_type='application/json; charset=utf-8')
    else:
        return Http404("This view is only reachable via an AJAX POST request.")


def get_counts(request):
    report_id = request.GET['report']
    report = Report.objects.get(id=report_id)

    records = report.queryset
    ctx = {
        'emails': records.emails,
        'calls': records.phone_calls,
        'meetings': records.meetings,
        'applications': records.applications,
        'interviews': records.interviews,
        'hires': records.hires,
        'communications': records.communication_activity.count(),
        'referrals': records.referrals,
        'contacts': list(records.contacts)}

    return HttpResponse(
        json.dumps(ctx), content_type='application/json; charset=utf-8')


class ReportView(View):
    app = 'mypartners'
    model = 'contactrecord'

    @method_decorator(company_has_access('prm_access'))
    def dispatch(self, *args, **kwargs):
        return super(ReportView, self).dispatch(*args, **kwargs)

    # view report
    def get(self, request):
        if request.is_ajax():
            report_id = request.GET.get('report', 0)
            report = Report.objects.get(id=report_id)
            report_graph = PRMReport(report)
            ctx = {
                "report": report_graph
            }

            response = HttpResponse()
            html = render_to_response('myreports/prm_report.html', ctx,
                                      RequestContext(request))
            response.content = html.content

            return response

    def post(self, request, *args, **kwargs):
        app = kwargs.get('app', 'mypartners')
        model = kwargs.get('model', 'contactrecord')
        # create_report(request, app, model)
        company = get_company_or_404(request)
        user = request.user
        params = parse_params(request.POST)

        params.pop('csrfmiddlewaretoken', None)
        name = params.pop('report_name', datetime.now())
        ignore_cache = params.pop('ignore_cache', False)
        records = filter_records(
            company, user, app, model, params, ignore_cache)

        contents = serialize('json', records)
        results = ContentFile(contents)
        report, created = Report.objects.get_or_create(
            name=name, created_by=user, owner=company, app=app, model=model,
            params=json.dumps(params))

        report.results.save('%s-%s.json' % (name, report.pk), results)

        return HttpResponse()


def download_report(request):
    # download report
    report_id = request.GET.get('id', 0)
    report = get_object_or_404(
        get_model('myreports', 'report'), pk=report_id)

    response = HttpResponse(content_type='text/csv')
    content_disposition = "attachment; filename=%s-%s.csv"
    response['Content-Disposition'] = content_disposition % (
        report.name, report.pk)

    records = humanize(report.python)
    response = serialize('csv', records, output=response)

    return response
