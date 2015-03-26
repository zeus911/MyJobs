from cStringIO import StringIO
import csv
import HTMLParser
import json
from itertools import chain

from django.core import serializers
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models.loading import get_model
from django.db.models.query import QuerySet
from django.utils.html import strip_tags
from mypartners.models import CONTACT_TYPE_CHOICES


# TODO:
# * finish humanizing other columns
# * allow other models to be humanized, maybe generalize the things being
# * humanized and create a Humanize object?
# Note: natural_key wasn't used because i'm already using a dict by the time I
#       get here.
def humanize(records):
    # TODO: This is getting silly. Bite the bullet and use natural keys on the
    #       next iteration
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
    contact_types = dict(CONTACT_TYPE_CHOICES)
    # convert tag ids to names
    tag_ids = set(chain.from_iterable(record['tags'] for record in records))
    tags = dict(get_model('mypartners', 'tag').objects.filter(
        pk__in=tag_ids).values_list('pk', 'name'))

    # convert partner ids to names
    partner_ids = [record['partner'] for record in records]
    partners = dict(get_model('mypartners', 'partner').objects.filter(
        pk__in=partner_ids).values_list('pk', 'name'))

    # convert user ids to names
    user_ids = [record['created_by'] for record in records]
    users = dict(get_model('myjobs', 'user').objects.filter(
        pk__in=user_ids).values_list('pk', 'email'))

    for record in records:
        # make tag lists look pretty
        record['tags'] = ', '.join([tags[tag] for tag in record['tags']])
        # get rid of pks
        record.pop('pk', None)
        # human readable contact types
        record['contact_type'] = contact_types[record['contact_type']]
        # human readable partners
        record['partner'] = partners.get(record['partner'], "")
        # human readable created by users
        record['created_by'] = users.get(record['created_by'], "")
        # strip extra newlines from notes and convert HTML entities
        record['notes'] = parser.unescape('\n'.join(
            ' '.join(line.split())
            for line in record['notes'].split('\n') if line))
        record['notes'] = '\n'.join(
            filter(bool, record['notes'].split('\n\n')))

        # get rid of None values
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


# TODO: Find a better way to handle counts
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
    if isinstance(data, QuerySet):
        data = [dict({'pk': record['pk']}, **record['fields'])
                for record in serializers.serialize('python', data)]

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
