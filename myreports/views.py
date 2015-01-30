from django.http import HttpResponse, Http404
from django.shortcuts import render_to_response
from django.template import RequestContext

from myreports.decorators import restrict_to_staff
from mypartners.models import Partner, Contact
from universal.helpers import get_company_or_404


@restrict_to_staff()
def reports(request):
    if request.is_ajax():
        response = HttpResponse()
        template = 'myreports/prm/page{page}.html'
        html = render_to_response(template.format(page=request.GET['page']),
                                  {}, RequestContext(request))
        response.content = html.content
        return response

    return render_to_response('myreports/reports.html', {},
                              RequestContext(request))


def prm_filter_partners(request):
    if request.is_ajax():
        company = get_company_or_404(request)
        partners = Partner.objects.filter(owner=company)
        data = {
            'partners': partners
        }
        response = HttpResponse()
        template = 'myreports/includes/prm/partners.html'
        html = render_to_response(template, data, RequestContext(request))
        response.content = html.content
        return response


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