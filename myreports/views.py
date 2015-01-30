import json

from django.core.serializers.json import DjangoJSONEncoder
from django.db.models.loading import get_model
from django.http import HttpResponse, Http404
from django.shortcuts import render_to_response
from django.template import RequestContext

from myreports.decorators import restrict_to_staff
from mypartners.models import Partner, Contact
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




def prm_filter_contacts(request):
    if request.is_ajax():
        company = get_company_or_404(request)
        partners = Partner.objects.filter(owner=company)
        contacts = Contact.objects.filter(partner__in=partners)
        data = {
            'contacts': contacts
        }
        response = HttpResponse()
        template = 'myreports/includes/prm/contacts.html'
        html = render_to_response(template, data, RequestContext(request))
        response.content = html.content
        return response
    else:
        raise Http404


def search_records(request, model='ContactRecord', output=None):
    # TODO: update documentation
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

    if request.is_ajax() and request.method == 'GET':
        company = get_company_or_404(request)

        # get rid of empty params and flatten single-item lists
        params = {}
        for key in request.GET.keys():
            value = request.GET.getlist(key)
            if value:
                if len(value) > 1:
                    params[key] = value
                else:
                    params[key] = value[0]

        records = get_model('mypartners', model.title()).objects.from_search(
            company, params)

        ctx = {'records': records}

        # serialize
        if output == 'json':
            # you can't use djangos serializers on a regular python object
            ctx['records'] = list(records.values())
            ctx = json.dumps(ctx, cls=DjangoJSONEncoder)

            return HttpResponse(ctx)
        else:
            template = 'myreports/includes/prm/partners.html'
            html = render_to_response(template, ctx, RequestContext(request))
            response = HttpResponse()
            response.content = html.content

            return response
    else:
        raise Http404("This view is only reachable via an AJAX POST request")
