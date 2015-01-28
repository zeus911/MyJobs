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
    """
    AJAX view that returns a JSON representation of a query set based on post
    data submitted with the request.

    If :model: is found in the request, it is assumed that we are filtering on
    that model, otherwise `ContactRecord` is assumed. The remaining query
    parameters should map directly onto the relevant model's fields.

    For example, the following should return all Contacts who are tagged as a
    veteran:

        client.post(model='Contact', tag='veteran')
    """

    if not request.is_ajax():
        return HttpResponse()

    params = {k:v for k, v in request.GET.items()}
    model = params.pop('model', 'ContactRecord')
    # TODO: think about moving these to model-specific 'search' functions
    # map models to appropriate helper functions
    get_records_for = {'Contact': filter_contacts,
                       'ContactRecord': filter_contact_records}

    records, types = get_records_for[model](request)

    ctx = {'records': records, 'types': types}

    return HttpResponse(ctx)
