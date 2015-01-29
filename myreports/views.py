import json

from django.core.serializers.json import DjangoJSONEncoder
from django.db.models.loading import get_model
from django.http import HttpResponse, Http404
from django.shortcuts import render_to_response
from django.template import RequestContext

from myreports.decorators import restrict_to_staff
from myreports.helpers import filter_contacts
from universal.helpers import get_company_or_404


@restrict_to_staff()
def reports(request):
    """The Reports app landing page."""

    return render_to_response('myreports/reports.html', {},
                              RequestContext(request))


def search_records(request):
    # TODO: Render a template with the results as a QuerySet
    """
    AJAX view that returns a JSON representation of a query set based on post
    data submitted with the request.

    Expected Query Parameters:
        :model: The model to filter on. Defaults to `ContactRecord`.
        :output: Output format for results. If not present, results are
                 returned as JSON.
        :start_date: Lower bound for record date-related field (eg. `datetime`
                     for `ContactRecord`).
        :end_date: Upper bound for record date-related field (eg. `datetime`
                   for `ContactRecord`).

        Remaining query parameters are assumed to be field names of the model.

    For example, the following should return all Contacts who are tagged as a
    veteran as JSON:

        client.post(model='Contact', tag='veteran', output='json')
    """

    if request.is_ajax() and request.method == 'POST':

        company = get_company_or_404(request)
        params = {key: value for key, value in request.POST.items() if key}
        model = params.pop('model', 'ContactRecord')
        output = params.pop('output', 'json')

        records = get_model('mypartners', model).objects.from_search(
            company, params)
        ctx = {'records': records}

        # serialize
        if output == 'json':
            # you can't use djangos serializers on a regular python object
            ctx['records'] = list(records.values())
            ctx = json.dumps(ctx, cls=DjangoJSONEncoder)

            return HttpResponse(ctx)
    else:
        raise Http404("This view is only reachable via an AJAX POST request")
