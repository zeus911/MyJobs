import json

from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext

from myreports.decorators import restrict_to_staff
from myreports.helpers import filter_contact_records, filter_contacts


@restrict_to_staff()
def reports(request):
    """The Reports app landing page."""

    return render_to_response('myreports/reports.html', {},
                              RequestContext(request))


def search_records(request):
    # TODO: Documentation 
    if not request.is_ajax():
        return HttpResponse()

    params = {k:v for k, v in request.GET.items()}
    model = params.pop('model', 'ContactRecord')
    get_records_for = {'Contact': filter_contacts,
                       'ContactRecord': filter_contact_records}

    records, types = get_records_for[model]()

    ctx = {'records': list(records.values_list('name', 'uri', 'tags')),
           'types': types}

    return HttpResponse(json.dumps(ctx))
