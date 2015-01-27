from datetime import datetime
import json

from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext

from mypartners.models import ContactRecord
from myreports.decorators import restrict_to_staff


@restrict_to_staff()
def reports(request):
    """The Reports app landing page."""

    return render_to_response('myreports/reports.html', {},
                              RequestContext(request))

def search_records(request):
    """
    AJAX view that returns `ContactRecord`s based on post data submitted with
    the request. Query parameters with the exceptions listed below should match
    `ContactRecord` field names.

    Field Types:
        DateTimeField - Handled in accordance with the exceptions listed below.
        CharField - Handled as an exact, case-insensitive match.
        TextField - Handled as a partial, case-insensitive match.
        AutoField - Handled as an exact match.
        ForeignKey - Handled as a partial, case-insensitive match.

    Exceptions:
    * `datetime` should instead be passed as `start_date` and `end_date`, which
       will then be pasred using a >= and <= match respectively. That is, if
       both are given, records that fall between those dates will be queried
       for.
    """

    if not request.is_ajax():
        return HttpResponse()


    # used to map field types to a query
    type_to_query = {
        'CharField': '__iexact',
        'TextField': '__icontains',
        'AutoField': '__exact',
        'ForeignKey': '__name__icontains'}

    records = ContactRecord.objects.all()
    types = {}

    for key, value in request.GET.items():
        if value:
            type_ = get_fieldtype_(ContactRecord, key)

            if key == 'start_date':
                value = datetime.strptime(value, '%m/%d/%Y').date()
                records.filter(datetime__gte=value)
            elif key == 'end_date':
                value = datetime.strptime(value, '%m/%d/%Y').date()
                records.filter(datetime__lte=value)
            elif type_:
                records.filter(**{type_ + type_to_query[type_]: value})
                types[key] = type_

    ctx = {'records': list(records.values_list('name', 'uri', 'tags')),
           'types': types}

    return HttpResponse(json.dumps(ctx))

# TODO: Move to helpers.py
def get_fieldtype_(model, field):
    """Returns the type of the `model`'s `field` or None if it doesn't exist."""

    fields = model.get_searchable_fields()
    if field in fields:
        return model._meta.get_field(field).get_internaltype_()
