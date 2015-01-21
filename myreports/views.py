from django.http import Http404
from django.shortcuts import render_to_response
from django.template import RequestContext


def reports_overview(request):
    if not request.user.is_staff:
        raise Http404
    return render_to_response('myreports/reports_overview.html', {},
                              RequestContext(request))