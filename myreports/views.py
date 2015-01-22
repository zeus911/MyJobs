from django.contrib.auth.decorators import user_passes_test
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext


@user_passes_test(lambda u: u.is_staff)
def reports_overview(request):
    return render_to_response('myreports/reports_overview.html', {},
                              RequestContext(request))

@user_passes_test(lambda u: u.is_staff)
def edit_report(request):
    return HttpResponse()
