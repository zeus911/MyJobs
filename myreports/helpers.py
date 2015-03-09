import json

from django.core import serializers
from django.core.serializers.json import DjangoJSONEncoder


def serialize(fmt, data, counts=None):
    if fmt == 'json':
        data = [dict({'pk': record['pk']}, **record['fields'])
                for record in serializers.serialize('python', data)]

        if counts:
            data = [dict({'count': counts[record['pk']]}, **record)
                    for record in data]

        return json.dumps(data, cls=DjangoJSONEncoder)
    else:
        return data
