from datetime import datetime
from urlparse import urlparse, urlunparse
from xml.sax.saxutils import escape

from django import template

from api.models import Onet


register = template.Library()


@register.simple_tag
def get_location(job):
    city = job.get('city', '')
    state = job.get('state', '')
    if city and state:
        location = "%s, %s" % (city, state)
    else:
        location = '%s%s' % (city, state)
    return escape(location)


@register.assignment_tag
def get_onets(job):
    onets = job.get('onet', None)
    if onets:
        return Onet.objects.filter(code__in=onets)
    else:
        return []


@register.filter
def job_datetime_format(value):
    try:
        date_created = datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ")
    except ValueError:
        date_created = datetime.strptime(value, "%Y-%m-%dT%H:%M:%S.%fZ")
    date_created = date_created.strftime('%Y-%-m-%-d %-I:%M %p')
    return date_created


@register.filter
def search_datetime_format(value):
    date_created = value.strftime('%-m/%-d/%Y %-I:%M:%S %p')
    return date_created


@register.filter
def readable_onet_code(onet_code):
    return "%s-%s.%s" % (onet_code[:2], onet_code[2:-2], onet_code[-2:])


@register.filter
def update_url(url):
    if not url:
        url = "http://us.jobs"
    else:
        url_parts = list(urlparse(url))
        url_parts[2] = url_parts[2].replace('/', '')
        url_parts[2] = '%s' % url_parts[2][:32]
        url_parts = tuple(url_parts)
        url = urlunparse(url_parts)
    return url