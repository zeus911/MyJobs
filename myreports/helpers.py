import json

from django.core import serializers
from django.core.serializers.json import DjangoJSONEncoder


def serialize(fmt, data, counts=None):
    # TODO: see if i can preserve annotations using `values`
    if fmt == 'json':
        data = [dict({'pk': record['pk']}, **record['fields'])
                for record in serializers.serialize('python', data)]

        if counts:
            data = [dict({'count': counts[record['pk']]}, **record)
                    for record in data]

        return json.dumps(data, cls=DjangoJSONEncoder)
    else:
        return data


def parse_params(querydict):
    params = {}
    for key in querydict.keys():
        value = querydict.get(key)
        value_list = querydict.getlist(key)

        # parsing a list parameter as a regular parameter only captures the
        # last item, so if trying both ways returns the same value, we can
        # be sure that it's not a list
        if value:
            if value == value_list[0]:
                params[key] = value
            else:
                # lists are not hashable
                params[key] = tuple(value_list)

    return params
