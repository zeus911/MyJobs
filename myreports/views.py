import json

from django.core import serializers
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models.loading import get_model
from django.db.models import Count
from django.http import HttpResponse, Http404
from django.shortcuts import render_to_response
from django.template import RequestContext

from myreports.decorators import restrict_to_staff
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


def filter_records(request,
                   app='mypartners', model='contactrecord', output='json'):
    """
    AJAX view that returns a query set based on post data submitted with the
    request, caching results by default.

    Inputs:
        :app: The app to which the model belongs.
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
        :ignore_cache: If present, this view's cache is ignored.
        :order_by: The field to sort records by. If not present, primary key is
                  used.
        :count: The field to annotate with a count. If not present, no
                annotations are used.

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
    if request.is_ajax() and request.method == 'POST':
        company = get_company_or_404(request)
        user = request.user
        path = request.get_full_path()

        # get rid of empty params and flatten single-item lists
        params = {}
        for key in request.POST.keys():
            value = request.POST.get(key)
            value_list = request.POST.getlist(key)

            # parsing a list parameter as a regular parameter only captures the
            # last item, so if trying both ways returns the same value, we can
            # be sure that it's not a list
            if value:
                if value == value_list[0]:
                    params[key] = value
                else:
                    # lists are not hashable
                    params[key] = tuple(value_list)

        # remove csrf token from search parameters
        params.pop('csrfmiddlewaretoken', None)

        # get special query parameters
        output = params.pop('output', 'json')
        ignore_cache = params.pop('ignore_cache', False)
        order_by = params.pop('order_by', None)
        count = params.pop('count', None)

        cache_key = (user, company, path, tuple(params.items()))
        # fetch results from cache if available
        if not ignore_cache and cache_key in filter_records.cache:
            records = filter_records.cache[cache_key]
            cached = True
        else:
            records = get_model(app, model).objects.from_search(
                company, params)

            if count:
                records = records.annotate(count=Count(count))

            if order_by:
                if hasattr(order_by, '__iter__'):
                    records = records.order_by(*order_by)
                else:
                    records = records.sort_by(order_by)

            cached = False
            filter_records.cache[cache_key] = records

        ctx = {'records': records, 'cached': cached}

        # serialize
        if output == 'python':
            return records
        elif output == 'json':

            # store the counts so we don't have to run a query every time later
            if count:
                counts = {record.pk: record.count for record in records}
            else:
                counts = None

            # flatten the structure; attempting to modify dicts in place while
            # serializing proved to be rather inefficient
            data = []
            for record in serializers.serialize('python', records):
                data.append(record['fields'])
                data[-1]['pk'] = record['pk']

                # using a serializer strips annotations, so we add them back in
                if counts:
                    data[-1]['count'] = counts[record['pk']]

            ctx['records'] = data
            ctx = json.dumps(ctx, cls=DjangoJSONEncoder)

            response = HttpResponse(
                ctx, content_type='application/json; charset=utf-8')
        else:
            html = render_to_response(
                output + ".html", ctx, RequestContext(request))
            response = HttpResponse()
            response.content = html.content

        return response
    else:
        raise Http404("This view is only reachable via an AJAX POST request")
filter_records.cache = {}


@company_has_access('prm_access')
def generate_report(request):
    records = filter_records(output='python')
