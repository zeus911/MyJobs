from cStringIO import StringIO
import csv
import HTMLParser
import json

from django.core import serializers
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models import query
from django.utils.html import strip_tags
from mypartners.models import CONTACT_TYPES


# TODO:
# * allow other models to be humanized, maybe generalize the things being
# * humanized and create a Humanize object?
def humanize(records):
    """
    Converts values in a dict to their human-readable counterparts. At the
    moment, this means converting tag ids to a list of tag names, removing the
    primary key, and converting contact types. As such, this is specifically
    only useful for contact records.

    Inputs:
        :records: `dict` of records to be humanized

    Outputs:
        The humanized records.
    """

    parser = HTMLParser.HTMLParser()

    for record in records:
        # make tag lists look pretty
        if 'tags' in record:
            record['tags'] = ', '.join(record['tags'])
        # get rid of pks
        record.pop('pk', None)
        # human readable contact types
        if 'contact_type' in record:
            record['contact_type'] = CONTACT_TYPES[record['contact_type']]
        # strip html and extra whitespace from notes
        if 'notes' in record:
            record['notes'] = parser.unescape('\n'.join(
                ' '.join(line.split())
                for line in record['notes'].split('\n') if line))
            # second pass to take care of extra new lines
            record['notes'] = '\n'.join(
                filter(bool, record['notes'].split('\n\n')))

        # get rid of nones
        if 'created_by' in record:
            record['created_by'] = record['created_by'] or ''
        if 'length' in record:
            record['length'] = record['length'] or ''

    return records


def parse_params(querydict):
    """
    Parses a `QueryDict` into a regular dict, discarding falsey values and
    flattening singleton lists.

    Inputs:
        :querydict: The `QueryDict` to be pasred (eg. request.GET).

    Outputs:
        A dictionary of non-empty parameters.
    """
    # get rid of empty params and flatten single-item lists
    params = {}
    for key in querydict.keys():
        value = tuple(filter(bool, querydict.getlist(key)))

        if len(value) == 1:
            value = value[0]

        params[key] = value

    return params


# TODO:
#   * find a better way to handle counts
#   * do something other than isinstance checks (duck typing anyone?)

def serialize(fmt, data, counts=None):
    """
    Like `django.core.serializers.serialize`, but produces a simpler structure
    and retains annotated fields*.

    Inputs:
        :fmt: The format to serialize to. Currently recognizes 'csv', 'json',
              and 'python'.
        :data: The data to be serialized.
        :counts: A dictionary mapping primary keys to actual counts. This is a
                 cludge which should be deprecated in later version of this
                 function if at all possible.

    Outputs:
        Either a Python object or a string represention of the requested
        format.

    * Currently, only count with values passed in manually through `counts`.
    """
    if isinstance(data, query.ValuesQuerySet):
        data = list(data)
    elif isinstance(data, query.QuerySet):
        data = [dict({'pk': record['pk']}, **record['fields'])
                for record in serializers.serialize(
                    'python', data, use_natural_keys=True)]

        if counts:
            data = [dict({'count': counts[record['pk']]}, **record)
                    for record in data]

    # strip HTML tags from string values
    for index, record in enumerate(data[:]):
        data[index] = {key: strip_tags(value) if isinstance(value, basestring)
                       else value for key, value in record.items()}

    if fmt == 'json':
        return json.dumps(data, cls=DjangoJSONEncoder)
    elif fmt == 'csv':
        output = StringIO()
        writer = csv.writer(output)
        columns = sorted(data[0].keys())
        writer.writerow([column.replace('_', ' ').title()
                         for column in columns])

        for record in data:
            writer.writerow([unicode(record[column]).encode('utf-8')
                             for column in columns])

        return output.getvalue()
    else:
        return data
