from datetime import datetime, timedelta
from django.core.serializers import serialize
from mypartners.models import Contact, ContactRecord


def filter_contact_records(request, output=None):
    # TODO: different export types
    """
    Examines the request for query parameters and converts those to sensible
    query terms. Parameters should generally match `ContactRecord` field
    names, though `start_date` and `end_date` are also accepted and will be
    mapped to the `datetime` field.

    Inputs:
        :request: The request object to inspect for search terms
        :output: The output format the results should be returned in

    Output:
        A tuple pair of the results and the types of the fields in those
        results.
    """

    # used to map field types to a query
    type_to_query = {
        'CharField': '__iexact',
        'TextField': '__icontains',
        'AutoField': '__exact',
        'ForeignKey': '__name__icontains'}

    # get all values that aren't falsey
    fields = {key: value for key, value in  request.GET.items() if value}
    start_date = fields.pop('start_date', None)
    end_date = fields.pop('end_date', None)

    # filter by dates
    records = ContactRecord.objects.all()
    if start_date:
        start_date = datetime.strptime(start_date, '%m/%d/%Y').date()
        records.filter(datetime__gte=start_date)

    if end_date:
        # handles off-by-one error; otherwise date provided is excluded
        end_date = datetime.strptime(end_date, '%m/%d/%Y').date() + timedelta(1)
        records.filter(datetime__lte=end_date)

    types = {}
    for key, value in fields.items():
        type_ = ContactRecord.get_field_type(key)

        if type_:
            # determine best query based on field type
            records.filter(**{type_ + type_to_query[type_]: value})
            types[key] = type_

    import ipdb; ipdb.set_trace()

    # convert to json
    if output:
        records = serialize(output, records)

    return records, types


def filter_contacts(request):
    # TODO: Build out function and write documentation
    return Contact.objects.all(), {}
