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

from myreports.helpers import humanize, parse_params, serialize
from myreports.models import Report
from universal.helpers import get_company_or_404
from universal.decorators import company_has_access


@company_has_access('prm_access')
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

    if request.is_ajax():
        response = HttpResponse()
        html = render_to_response('myreports/report_overview.html', ctx,
                                  RequestContext(request)).content
        response.content = html
        return response

    return render_to_response('myreports/reports.html', ctx,
                              RequestContext(request))


@company_has_access('prm_access')
def report_archive(request):
    if request.is_ajax():
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


@company_has_access('prm_access')
def view_records(request, app, model):
    """
    Returns records as JSON.

    Inputs:
        :request: Request object to inspect for search parameters.
        :app: Application to query.
        :model: Model to query.

    Output:
       A JSON response containing the records queried for.
    """
    if request.is_ajax() and request.method == 'GET':
        company = get_company_or_404(request)

        # parse request into dict, converting singleton lists into single items
        params = parse_params(request.GET)

        # remove non-query related params
        params.pop('csrfmiddlewaretoken', None)
        count = params.pop('count', None)
        values = params.pop('values', [])

        records = get_model(app, model).objects.from_search(
            company, params)

        counts = {}
        if count:
            records = records.annotate(count=Count(count, distinct=True))
            counts = {record.pk: record.count for record in records}

        ctx = serialize('json', records, counts=counts, values=values)

        response = HttpResponse(
            ctx, content_type='application/json; charset=utf-8')

        return response
    else:
        raise Http404("This view is only reachable via an AJAX GET request.")


@company_has_access('prm_access')
def get_inputs(request):
    if request.is_ajax() and request.method == "GET":
        report_id = request.GET.get('id', 0)
        report = get_object_or_404(Report, pk=report_id)
        return HttpResponse(
            report.params, content_type='application/json; charset=utf-8')
    else:
        return Http404("This view is only reachable via an AJAX GET request.")


class ReportView(View):
    """View for managing report objects."""

    app = 'mypartners'
    model = 'contactrecord'

    @method_decorator(company_has_access('prm_access'))
    def dispatch(self, *args, **kwargs):
        return super(ReportView, self).dispatch(*args, **kwargs)

    def get(self, request, **kwargs):
        """
        Get a report by ID and return interesting numbers as a JSON
        response. The only expected query parameter is 'id'.
        """
        if request.method == 'GET':
            report_id = request.GET.get('id', 0)
            report = Report.objects.get(id=report_id)
            records = report.queryset

            ctx = {
                'emails': records.emails,
                'calls': records.calls,
                'searches': records.searches,
                'meetings': records.meetings,
                'applications': records.applications,
                'interviews': records.interviews,
                'hires': records.hires,
                'communications': records.communication_activity.count(),
                'referrals': records.referrals,
                'contacts': list(records.contacts)}

            return HttpResponse(
                json.dumps(ctx),
                content_type='application/json; charset=utf-8')
        else:
            raise Http404(
                "This view is only reachable via a GET request.")

    def post(self, request, app='mypartners', model='contactrecords'):
        """
        Create a report by querying on a specific model.

        The request's POST data is parsed for parameters to pass to the model's
        `from_search` method.

        Inputs:
            :app: The app to which the model belongs.
            :model: The model to query on

        Outputs:
           An HttpResponse indicating success or failure of report creation.
        """

        if request.method == 'POST':
            company = get_company_or_404(request)
            params = parse_params(request.POST)

            params.pop('csrfmiddlewaretoken', None)
            name = params.pop('report_name', datetime.now())

            records = get_model(app, model).objects.from_search(
                company, params)

            contents = serialize('json', records)
            results = ContentFile(contents)
            report, created = Report.objects.get_or_create(
                name=name, created_by=request.user,
                owner=company, app=app, model=model,
                params=json.dumps(params))

            report.results.save('%s-%s.json' % (name, report.pk), results)

            return HttpResponse(name, content_type='text/plain')
        else:
            raise Http404(
                "This view is only reachable via a POST request.")


@company_has_access('prm_access')
def downloads(request):
    report_id = request.GET.get('id', 0)
    report = get_object_or_404(
        get_model('myreports', 'report'), pk=report_id)

    fields = [field for field in report.python[0].keys() if field != 'pk']

    values = json.loads(report.values) or fields
    columns = {field.replace('_', ' ').title(): field in values
               for field in fields}

    ctx = {'columns': columns}

    return render_to_response('myreports/report-download.html', ctx,
                              RequestContext(request))


@company_has_access('prm_access')
def download_report(request):
    """Download report as csv."""

    report_id = request.GET.get('id', 0)
    values = request.GET.getlist('values', None)

    report = get_object_or_404(
        get_model('myreports', 'report'), pk=report_id)

    if values:
        report.values = json.dumps(values)
        report.save()

    records = humanize(report.python)

    response = HttpResponse(content_type='text/csv')
    content_disposition = "attachment; filename=%s-%s.csv"
    response['Content-Disposition'] = content_disposition % (
        report.name, report.pk)

    response.write(serialize('csv', records, values=values))

    return response
