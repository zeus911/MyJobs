from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext

from myreports.decorators import restrict_to_staff


@restrict_to_staff()
def reports(request):
    return render_to_response('myreports/reports.html', {},
                              RequestContext(request))
