from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext

from myreports.decorators import restrict_to_staff


@restrict_to_staff()
def reports_overview(request):
    return render_to_response('myreports/reports_overview.html', {},
                              RequestContext(request))

@restrict_to_staff()
def edit_report(request):
    return render_to_response('myreports/create_report.html', {},
                              RequestContext(request))
