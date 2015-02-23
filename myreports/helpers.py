import bleach
import csv
import json

from django.core import serializers
from django.core.serializers.json import DjangoJSONEncoder
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils.html import strip_tags


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
        content_disposition = "attachment; filename=%s.csv" % model.replace(
            ' ', '_')
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = content_disposition

        writer = csv.writer(response)
        writer = csv.DictWriter(response, sorted(data[0].keys()))
        writer.writeheader()

        FIELDS_TO_STRIP = ['notes']
        for record in data:
            # strip tags from fields which contain them, otherwise convert to
            # unicode and write to CSV
            writer.writerow({
                key: unicode(strip_tags(value)).encode('utf-8')
                if key in FIELDS_TO_STRIP else unicode(value).encode('utf-8')
                for key, value in sorted(record.items())})

        return response

    else:
        html = render_to_response(
            output + ".html", context, RequestContext(request))
        response = HttpResponse()
        response.content = html.content

    return response
