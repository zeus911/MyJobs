from datetime import datetime, timedelta
from mypartners.models import Contact, ContactRecord


def filter_contact_records(parameters):
    """
    Inputs:
        :parameters: A dict of field: term pairs where field is a field of the
                     `ContactRecord` model and term is search term you'd like
                     to filter against.

                     For `datetime`, pass `start_date` and/or `end_date`
                     instead.
    """

    # extract dates so they aren't traversed later
    start_date = parameters.pop('start_date', None)
    end_date = parameters.pop('end_date', None)

    # used ot map field types to a query
    type_to_query = {
        'CharField': '__iexact',
        'TextField': '__icontains',
        'AutoField': '__exact',
        'ForeignKey': '__name__icontains'}

    # filter by dates
    records = ContactRecord.objects.all()
    if start_date:
        start_date = datetime.strptime(start_date, '%m/%d/%Y').date()
        records.filter(datetime__gte=start_date)

    if end_date:
        # handles off-by-one error; otherwise date provided is excluded
        end_date = datetime.strptime(end_date, '%m/%d/%Y').date() + timedelta(1)
        records.filter(datetime__lte=end_date)

    for key, value in parameters.items():
        type_ = ContactRecord.get_field_type(key)

        if type_:
            records = records.filter(
                **{'%s%s' % (key, type_to_query[type_]): value})

    return records


def filter_contacts(request):
    # TODO: Build out function and write documentation
    return Contact.objects.all(), {}
