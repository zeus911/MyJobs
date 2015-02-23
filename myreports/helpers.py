import csv
import json

from django.core import serializers
from django.core.serializers.json import DjangoJSONEncoder
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext


# TODO:
#   * documentation
#   * xml and print friendly output
def render_response(request, context, output=None):
    model = context['records'].model._meta.verbose_name_plural

    if output in ['json', 'csv']:
        # The built-in JSON serializer is a bit verbose, so we instead extract
        # the fields we are interested in by serializing to Python, then
        # serialize that to JSON instead.
        data = [record['fields'] for record in serializers.serialize(
                'python', context['records'], use_natural_keys=True)]
    # serialize
    if output == 'json':
        ctx = json.dumps(context, cls=DjangoJSONEncoder)

        response = HttpResponse(ctx, content_type='application/json')
    elif output == 'csv':
        # TODO: use plural for model
        content_disposition = "attachment; filename='%s.csv'" % model
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = content_disposition

        writer = csv.writer(response)
        writer = csv.DictWriter(response, data[0].keys())
        writer.writeheader()

        for record in data:
            writer.writerow({
                key: unicode(value).encode('utf-8')
                for key, value in record.items()})

        return response

    else:
        html = render_to_response(
            output + ".html", context, RequestContext(request))
        response = HttpResponse()
        response.content = html.content

    return response
