import json

from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext

from mypartners.models import ContactRecord
from myreports.decorators import restrict_to_staff


@restrict_to_staff()
def reports(request):
    return render_to_response('myreports/reports.html', {},
                              RequestContext(request))

def search_records(request):
    if not request.is_ajax():
        return HttpResponse()


    # incrementally filter results
    records = ContactRecord.objects.all()
    fields = ContactRecord.get_searchable_fields()
    types = {field: get_field_type(ContactRecord, field) for field in fields}

    # TODO: Do something more sensible for date fields
    type_to_query = {
        'DateTimeField': '__gte',
        'CharField': '__iexact',
        'TextField': '__icontains',
        'AutoField': '__iexact',
        'ForeignKey': '__name__icontains'}

    for field, type_ in types.items():
        value = request.POST.get(field)
        if value:
            records.filter(**{type_ + type_to_query[type_]: value})

    ctx = {'records': list(results.values_list('name', 'uri', 'tags')),
           'types': types}

    return HttpResponse(json.dumps(ctx))

# TODO: Move to helpers.py
def get_field_type(model, field):
    return model._meta.get_field(field).get_internal_type()
