from collections import OrderedDict
from cStringIO import StringIO
import csv
import HTMLParser
import json

from django.core import serializers
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models import query
from lxml import html
from mypartners.models import CONTACT_TYPES


# TODO:
# * allow other models to be humanized, maybe generalize the things being
# * humanized and create a Humanize object?
def humanize(records):
    """
    Converts values in a dict to their human-readable counterparts. At the
    moment, this means converting tag ids to a list of tag names, and
    converting contact types. As such, this is specifically only useful for
    contact records.

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
        # human readable contact types
        if 'contact_type' in record:
            record['contact_type'] = CONTACT_TYPES[record['contact_type']]
        # strip html and extra whitespace from notes
        if 'notes' in record:
            # TODO: Find a faster way to do this
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

        if value == 'false':
            value = False
        elif value == 'true':
            value = True

        params[key] = value

    return params


# TODO:
#   * do something other than isinstance checks (duck typing anyone?)
def serialize(fmt, data, values=None, order_by=None):
    """
    Like `django.core.serializers.serialize`, but produces a simpler structure
    and retains annotated fields.

    Inputs:
        :fmt: The format to serialize to. Currently recognizes 'csv', 'json',
              and 'python'.
        :data: The data to be serialized.
        :values: The fields to include in the serialized output.
        :order_by: The field to sort the serialized records by.

    Outputs:
        Either a Python object or a string represention of the requested
        format.

    """

    if isinstance(data, query.ValuesQuerySet):
        data = list(data)
    elif isinstance(data, query.QuerySet):
        data = [dict({'pk': record['pk']}, **record['fields'])
                for record in serializers.serialize(
                    'python', data, use_natural_keys=True, fields=values)]

    if data:
        values = values or sorted(data[0].keys())
        order_by = order_by or values[0]
        _, reverse, order_by = sorted(order_by.partition('-'))

        # Convert data to a list of `OrderedDict`s,
        data = sorted([OrderedDict([(
            # strip HTML from invidual values...
            value, html.fromstring(record[value]).text_content()
            # if they aren't empty strings.
            if isinstance(record[value], basestring) and record[value].strip()
            else record[value]) for value in values]) for record in data],
                # and sort them by specified value (first column by default)
                key=lambda record: record[order_by], reverse=bool(reverse))

    if fmt == 'json':
        return json.dumps(data, cls=DjangoJSONEncoder)
    elif fmt == 'csv':
        output = StringIO()
        writer = csv.writer(output)
        columns = data[0].keys()
        writer.writerow([column.replace('_', ' ').title()
                         for column in columns])

        for record in data:
            writer.writerow([unicode(record[column]).encode('utf-8')
                             for column in columns])

        return output.getvalue()
    else:
        return data
