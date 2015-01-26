import json

from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext

from mypartners.models import Partner
from myreports.decorators import restrict_to_staff


@restrict_to_staff()
def reports(request):
    return render_to_response('myreports/reports.html', {},
                              RequestContext(request))

def filter_partners(request):
    #TODO: use contact records
    if not request.is_ajax():
        return HttpResponse()

    # get search parameters
    name, uri, tags = [request.GET.get(param, None) for param in [
        'name', 'uri', 'tags']]

    # incrementally filter results
    results = Partner.objects.all()
    types = {field: get_field_type(Partner, field) for field in ['name', 'uri', 'tags']}

    if name:
        results.filter(name__icontains=name)

    if uri:
        results.filter(uri__iexact=uri)

    if tags:
        tags = [tag.strip() for tag in tags.split(",")]
        for tag in tags:
            results.filter(tags__icontains=tag)

    ctx = {'results': results, 'types': types}

    return HttpResponse(json.dumps(ctx))

# TODO: Move to helpers.py
def get_field_type(model, field):
    return model._meta.get_field(field).get_internal_type()
