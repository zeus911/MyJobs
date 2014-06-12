from itertools import groupby
import uuid

from django import template
from urlparse import urlparse
from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe

from mydashboard.helpers import update_url_param
from myjobs.models import User
from myjobs.templatetags.common_tags import str_to_date
from myprofile.models import ProfileUnits, Name

register = template.Library()


@register.filter(name='get_distinct_users')
def get_distinct_users(values):
    # Get list of users who have searches for a specific microsite
    # Prepare structure for the addition of user names
    users = dict((search.user, False) for search in values)

    # Get list of primary names for the above users
    names = Name.objects.filter(user__in=users.keys(), primary=True)
    for name in names:
        # Associate each name with its owning user
        users[name.user] = name.get_full_name()

    return users


@register.filter(name='url_domain')
def url_domain(value):
    """
    Retrieve the given url from the candidate activity and returns a netloc
    version of the url

    Inputs:
    :value: url that candidate has for the saved search

    Outputs:
    :updated_url.netloc: url netloc
    """
    active_url = value

    if active_url.find('//') == -1:
        active_url = '//' + value

    updated_url = urlparse(active_url)

    return updated_url.netloc


@register.simple_tag(takes_context=True)
def get_candidate_query_string(context, company_id, user_id):
    current_url = context['request'].build_absolute_uri()
    data = {
        'company': str(company_id),
        'user': str(user_id),
    }
    for key, value in data.items():
        current_url = update_url_param(current_url, key, value)

    return "?%s" % urlparse(current_url).query


@register.simple_tag
def display_activity(candidate):
    """
    Format one document of analytics data for display on the candidate
    dashboard
    """
    activities = {
        'listing': [u'<strong>Job view</strong>',
                    u'{title}',
                    u'{domain}',
                    u'{date}'],
        'results': [u'<strong>Job search</strong>',
                    u'{query} {location}',
                    u'{domain}',
                    u'{date}'],
        'home': [u'<strong>Microsite view</strong>',
                 u'{domain}',
                 u'{date}'],
        'redirect': [u'<strong>Apply click</strong>',
                     u'<a href="http://my.jobs/{guid}">{guid}</a>',
                     u'{date}']
    }

    activity = activities.get(candidate.page_category, [])
    title = getattr(candidate, 'job_view_title', u'')
    domain = getattr(candidate, 'domain', u'')
    query = getattr(candidate, 'search_query', u'')
    location = getattr(candidate, 'search_location', u'')
    guid = getattr(candidate, 'job_view_guid', u'')

    if not query:
        query = 'All jobs'
    query = u'{query}'.format(query=conditional_escape(query))
    if location:
        location = u'in {location}'.format(
            location=conditional_escape(location))

    activity = [
        line.format(title=conditional_escape(title),
                    domain=conditional_escape(domain),
                    date=str_to_date(candidate.view_date),
                    query=query,
                    location=location,
                    guid=conditional_escape(guid))
        for line in activity
    ]
    activity_str = u'<br />'.join(activity)
    return mark_safe(activity_str)
