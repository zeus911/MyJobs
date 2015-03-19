from cStringIO import StringIO
import csv
import json
from itertools import chain

from django.core import serializers
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models.loading import get_model
from django.db.models.query import QuerySet
from django.utils.html import strip_tags
from mypartners.models import CONTACT_TYPE_CHOICES


def humanize(records):
    # TODO:
    # * finish humanizing other columns
    # * allow other models to be humanized, maybe generalize the things being
    # * humanized and create a Humanize object?

    # convert tag ids to names
    contact_types = dict(CONTACT_TYPE_CHOICES)
    tag_ids = set(chain.from_iterable(record['tags'] for record in records))
    tags = dict(get_model('mypartners', 'tag').objects.filter(
        pk__in=tag_ids).values_list('pk', 'name'))

    for record in records:
        # make tag lists look pretty
        record['tags'] = ', '.join([tags[tag] for tag in record['tags']])
        # get rid of pks
        record.pop('pk', None)
        # human readible contact types
        record['contact_type'] = contact_types[record['contact_type']]

    return records


def parse_params(querydict):
    # get rid of empty params and flatten single-item lists
    params = {}
    for key in querydict.keys():
        value = tuple(querydict.getlist(key))
        if len(value) == 1:
            value = value[0]

        params[key] = value

    return params


def serialize(fmt, data, output=None, counts=None):
    if isinstance(data, QuerySet):
        data = [dict({'pk': record['pk']}, **record['fields'])
                for record in serializers.serialize('python', data)]

        if counts:
            data = [dict({'count': counts[record['pk']]}, **record)
                    for record in data]

    for index, record in enumerate(data[:]):
        data[index] = {key: strip_tags(value) if isinstance(value, basestring)
                       else value for key, value in record.items()}

    if fmt == 'json':
        return json.dumps(data, cls=DjangoJSONEncoder)
    elif fmt == 'csv':
        output = output or StringIO()
        writer = csv.writer(output)
        columns = sorted(data[0].keys())
        writer.writerow([column.replace('_', ' ').title()
                         for column in columns])

        for record in data:
            writer.writerow([unicode(record[column]).encode('utf-8')
                             for column in columns])

        return output
    else:
        return data
