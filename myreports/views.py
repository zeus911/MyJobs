import json

from django.core.serializers.json import DjangoJSONEncoder
from django.db.models.loading import get_model
from django.http import HttpResponse, Http404
from django.shortcuts import render_to_response
from django.template import RequestContext

from myreports.decorators import restrict_to_staff
from universal.helpers import get_company_or_404


@restrict_to_staff()
def reports(request):
    """The Reports app landing page."""
    if request.is_ajax():
        response = HttpResponse()
        template = 'myreports/prm/page{page}.html'
        html = render_to_response(template.format(page=request.GET['page']),
                                  {}, RequestContext(request))
        response.content = html.content
        return response

    return render_to_response('myreports/reports.html', {},
                              RequestContext(request))


def filter_records(request, model='contactrecord', output='json'):
    """
    AJAX view that returns a query set based on post data submitted with the
    request, caching results by default.

    Inputs:
        :model: The model that should be filtered on.
        :output: The output type. By default, this is JSON. Alternatively the
                 path to a template file may be used, in which case the view is
                 rendered with 'records' passed as context.

    Output:
        An `output` appropriate object. For JSON, an object with a 'records'
        field is returned. For templates, an `HttpResponse` with a context
        object containing 'records' is returned.

    Query Parameters:
        :start_date: Lower bound for record date-related field (eg. `datetime`
                     for `ContactRecord`).
        :end_date: Upper bound for record date-related field (eg. `datetime`
                   for `ContactRecord`).
        :clear_cache: If present, this view's cache is cleared.

        Remaining query parameters are assumed to be field names of the model.

    Examples:
        The following should return all Contacts who are tagged as with
        'veteran' as JSON:

            client.post(reverse('filter_records', kwargs={'model': 'contact'}),
                        tag=['veteran'])

        The following will return a response using a template that includes all
        partners:

            client.post(reverse('filter_records', kwargs={
                'model': 'partner',
                'output': 'myreports/example_view.html'}))
    """
    if request.is_ajax() and request.method == 'GET':
        company = get_company_or_404(request)

        # get rid of empty params and flatten single-item lists
        params = {}
        for key in request.GET.keys():
            if key == 'clear_cache':
                filter_records.cache = {}
                continue

            value = request.GET.getlist(key)
            if value:
                if len(value) > 1:
                    params[key] = value
                elif value[0]:
                    params[key] = value[0]

        # fetch results from cache if available
        records = filter_records.cache.get(
            model, get_model(
                'mypartners', model).objects).from_search(
                    company, params)

        filter_records.cache[model] = records

        ctx = {'records': records}

        # serialize
        if output == 'json':
            # you can't use djangos serializers on a regular python object
            ctx['records'] = list(records.values())
            ctx = json.dumps(ctx, cls=DjangoJSONEncoder)

            return HttpResponse(ctx)
        else:
            html = render_to_response(output, ctx, RequestContext(request))
            response = HttpResponse()
            response.content = html.content

            return response
    else:
        raise Http404("This view is only reachable via an AJAX POST request")
filter_records.cache = {}
