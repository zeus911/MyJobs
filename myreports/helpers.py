from datetime import datetime, timedelta
from mypartners.models import Contact, ContactRecord


def filter_contact_records(request):
    """
    Examines the request for query parameters and converts those to sensible
    query terms. Parameters should generally match `ContactRecord` field
    names, though `start_date` and `end_date` are also accepted and will be
    mapped to the `datetime` field.
    """

    # used to map field types to a query
    type_to_query = {
        'CharField': '__iexact',
        'TextField': '__icontains',
        'AutoField': '__exact',
        'ForeignKey': '__name__icontains'}

    records = ContactRecord.objects.all()
    types = {}

    # save myself a check for a falsey value by removing them to begin with
    for key, value in {k:v for k, v in request.GET.items() if v}:
        type_ = ContactRecord.get_field_type(key)

        if key == 'start_date':
            value = datetime.strptime(value, '%m/%d/%Y').date()
            records.filter(datetime__gte=value)
        elif key == 'end_date':
            # handles off-by-one error; otherwise date provided is excluded
            value = datetime.strptime(
                value, '%m/%d/%Y').date() + timedelta(1)
            records.filter(datetime__lte=value)
        elif type_:
            # determine best query based on field type
            records.filter(**{type_ + type_to_query[type_]: value})
            types[key] = type_

    return records, types


def filter_contacts(request):
    # TODO: Build out function and write documentation
    return Contact.objects.all(), {}
